import math
from graphql import GraphQLError
from  ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
from datetime import timedelta 
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import smtplib
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def calculatePercentile(percentile_rank, response_time):
    # Number of response times
    num_responses = len(response_time)
    if num_responses<1:
        raise GraphQLError("No response time available")
    # Calculate the percentile position (index)
    position = (percentile_rank / 100) * (num_responses + 1)
    
    # Sort the response times
    sorted_times = sorted(response_time)
    
    # Find the value at the floor position (lower bound)
    lower_bound_value = sorted_times[math.floor(position) - 1]
    
    # Find the value at the ceil position (upper bound), handle index out of range
    upper_bound_value = sorted_times[math.ceil(position) - 1] if math.ceil(position) < num_responses else lower_bound_value
    # Calculate the percentile using interpolation
    percentile_value = lower_bound_value + (position - math.floor(position)) * (upper_bound_value - lower_bound_value)
    
    return percentile_value

def calculateMetrices(apiMetrices, query_name):
    try:
        
        total_no_of_requests = apiMetrices.count()
        if total_no_of_requests == 0:
            raise GraphQLError("No data available for the given API.")
 
        # Predefine variables
        availability_uptime = 0.0
        total_successful_requests = 0.0
        total_failed_requests = 0
        time_difference = 0.0
        latency_per_metrices = []
        response_size_per_metrices = []
        first_byte_time = []
        response_time = []
 
        # Common data fetching for metrics
        if query_name in ['availability_uptime', 'downtime']:
            total_uptime_requests = apiMetrices.filter(statusCode__gte=200, statusCode__lt=400).count()
            availability_uptime = round((total_uptime_requests / total_no_of_requests) * 100, 2)
              
 
        if query_name in ['success_count', 'success_rates']:
            total_successful_requests = apiMetrices.filter(statusCode=200).count()
 
        if query_name in ['error_count', 'error_rates']:
            total_failed_requests = apiMetrices.filter(statusCode__gte=400, statusCode__lt=600).count()
 
        if query_name in ['throughput', 'downtime']:
            timestamps = apiMetrices.values_list('timestamp', flat=True)
            oldest_timestamps = min(timestamps)
            recent_timestamps = max(timestamps)
            time_difference = (recent_timestamps - oldest_timestamps).total_seconds()
 
        if query_name == 'avg_latency':
            latency_per_metrices = list(apiMetrices.values_list('firstByteTime', 'requestStartTime'))
            latency_per_metrices = [(latency - request_start) for latency, request_start in latency_per_metrices]
 
        if query_name == 'avg_response_size':
            response_size_per_metrices = list(apiMetrices.values_list('responseSize', flat=True))
 
        if query_name == 'avg_first_byte_time':
            first_byte_time = list(apiMetrices.values_list('firstByteTime', flat=True))
 
        if query_name in ['response_time', 'percentile_50', 'percentile_90', 'percentile_99']:
            response_time = list(apiMetrices.values_list('responseTime', flat=True))
 
        # Percentile calculations
        if query_name in ['percentile_50', 'percentile_90', 'percentile_99']:
            percentile_value = int(query_name.split('_')[1])
            currentPercentile = calculatePercentile(percentile_value, response_time)
            new_response_time_list = response_time if len(response_time) == 1 else response_time[:-1]
            previousPercentile = calculatePercentile(percentile_value, new_response_time_list)
            percentageDiff = -1 * (((currentPercentile - previousPercentile) / previousPercentile) * 100)
 
        # Return metrics with calculations
        return {
            'availability_uptime': availability_uptime,
            'success_rates': round((total_successful_requests / total_no_of_requests) * 100, 2) if total_no_of_requests>0 else 0,
            'error_rates': round((total_failed_requests / total_no_of_requests) * 100, 2) if total_no_of_requests>0 else 0,
            'throughput': round((total_no_of_requests / (time_difference / 60.0)), 3) if time_difference>0.0 else 0,  # requests per minute
            'avg_latency': round(sum(latency_per_metrices,timedelta(0)).total_seconds() / len(latency_per_metrices), 2) if len(latency_per_metrices)>0 else 0,
            'downtime': round((time_difference) * ((100 - availability_uptime) / 100), 2) if availability_uptime < 100.00 else 0.0,
            'success_count': total_successful_requests,
            'error_count': total_failed_requests,
            'avg_response_size': round(sum(response_size_per_metrices) / len(response_size_per_metrices), 2) if len(response_size_per_metrices)>0 else 0,
            'avg_first_byte_time': round(sum(fbt.timestamp() for fbt in first_byte_time) / len(first_byte_time), 2) if len(first_byte_time)>0 else 0,
            'response_time': response_time,
            'percentile_50': {'curr_percentile_res_time': currentPercentile, 'percentage_diff': percentageDiff} if query_name == 'percentile_50' else None,
            'percentile_90': {'curr_percentile_res_time': currentPercentile, 'percentage_diff': percentageDiff} if query_name == 'percentile_90' else None,
            'percentile_99': {'curr_percentile_res_time': currentPercentile, 'percentage_diff': percentageDiff} if query_name == 'percentile_99' else None,
        }
 
    except GraphQLError as gql_error:
        raise gql_error
    except Exception as e:
        raise GraphQLError(f"Unknown error occured!")

def resolve_metrics(self, info):
        filtered_metrices = APIMetrics.objects.filter(api=self)
        from_date = info.context.from_date
        to_date = info.context.to_date

        if from_date:
            filtered_metrices = filtered_metrices.filter(timestamp__gte = from_date)
        if to_date:
            filtered_metrices = filtered_metrices.filter(timestamp__lte = to_date)  

        metrics = calculateMetrices(filtered_metrices.order_by('timestamp'), info.field_name)
        return metrics

def SendEmailNotification(serviceId):
    try:
        # Fetch the monitored API object along with related data
        service = MonitoredAPI.objects.select_related('businessUnit', 'subBusinessUnit').get(pk=serviceId)
        apiMetrices = APIMetrics.objects.filter(api=service)

        if service:
            # Extract recipient emails
            businessUnitDl = service.businessUnit.businessUnitDl
            subBusinessUnitDl = service.subBusinessUnit.subBusinessUnitDl
            receiverEmail = service.recipientDl

            # Email details
            subject = "API Monitoring Task Failed"
            from_email = settings.EMAIL_HOST_USER
            to_email = [receiverEmail]
            cc_email = [businessUnitDl, subBusinessUnitDl]

            # Calculate metrics
            context = {
                'apiName': service.apiName,
                'apiUrl':service.apiUrl,
                'availability_uptime': calculateMetrices(apiMetrices, 'availability_uptime')['availability_uptime'],
                'success_count': calculateMetrices(apiMetrices, 'success_count')['success_count'],
                'avg_latency': calculateMetrices(apiMetrices, 'avg_latency')['avg_latency'],
                'throughput': calculateMetrices(apiMetrices, 'throughput')['throughput'],
                'success_rates': calculateMetrices(apiMetrices, 'success_rates')['success_rates'],
                'error_count': calculateMetrices(apiMetrices, 'error_rates')['error_rates']
            }


            # Render email content
            html_content = render_to_string('emails/notification_email.html', context)
            html_msg = strip_tags(html_content)

            # Prepare email
            email = EmailMultiAlternatives(
                subject=subject,
                body=html_msg,
                from_email=from_email,
                to=to_email,
                cc=cc_email
            )
            email.attach_alternative(html_content, 'text/html')
            email.send(fail_silently=False)


    except MonitoredAPI.DoesNotExist:
        print(f'Monitored API with ID {serviceId} does not exist.')
    
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPRecipientsRefused, 
            smtplib.SMTPSenderRefused, smtplib.SMTPDataError, 
            smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, 
            TimeoutError) as e:
        print(f"SMTP Error: {str(e)}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
     
def get_service(serviceId):
    try:
        return MonitoredAPI.objects.select_related('businessUnit', 'subBusinessUnit').get(pk=serviceId)
    except MonitoredAPI.DoesNotExist:
        print(f'Monitored API with ID {serviceId} does not exist.')
        return None

def PrepareContext(apiMetrices, apiName, apiUrl):
    return {
        'apiName':apiName,
        'apiUrl':apiUrl,
        'availability_uptime': calculateMetrices(apiMetrices, 'availability_uptime')['availability_uptime'],
        'success_count': calculateMetrices(apiMetrices, 'success_count')['success_count'],
        'avg_latency': calculateMetrices(apiMetrices, 'avg_latency')['avg_latency'],
        'throughput': calculateMetrices(apiMetrices, 'throughput')['throughput'],
        'success_rates': calculateMetrices(apiMetrices, 'success_rates')['success_rates'],
        'error_count': calculateMetrices(apiMetrices, 'error_rates')['error_rates']
    }

def send_email(service, context):
    subject = "API Monitoring Task Failed"
    from_email = settings.EMAIL_HOST_USER
    to_email = ['rjnsaurabh143@gmail.com']
    cc_email = [service.businessUnit.businessUnitDl, service.subBusinessUnit.subBusinessUnitDl]


    html_content = render_to_string('emails/notification_email.html', context)
    html_msg = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=html_msg,
        from_email=from_email,
        to=to_email,
        cc=cc_email
    )
    email.attach_alternative(html_content, 'text/html')
    
    try:
        email.send(fail_silently=False)
        print("Email sent successfully.")
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPRecipientsRefused, 
            smtplib.SMTPSenderRefused, smtplib.SMTPDataError, 
            smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, 
            TimeoutError) as e:
        print(f"SMTP Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred while sending email: {str(e)}")


def SendEmailNotification(serviceId):
    service = get_service(serviceId)
    if not service:
        return

    apiMetrices = APIMetrics.objects.filter(api=service)
    context = PrepareContext(apiMetrices,service.apiName, service.apiUrl)

    send_email(service, context)
