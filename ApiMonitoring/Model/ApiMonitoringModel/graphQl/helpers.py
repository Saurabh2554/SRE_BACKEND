import math
from graphql import GraphQLError
from  ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from ApiMonitoring.Model.ApiMonitoringModel.assertionAndLimitModels import AssertionAndLimit
from datetime import timedelta 
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import smtplib
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests
import json
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

def calculatePercentile(percentile_rank, response_time_dict_list):
    # Number of response times
    
    num_responses = len(response_time_dict_list)
    if num_responses<1:
        raise GraphQLError("No response time available")
    # Calculate the percentile position (index)
    position = (percentile_rank / 100) * (num_responses + 1)
    
    # Sort the response times
    sorted_times = sorted(response_time_dict_list, key=lambda x: x['responsetime'] )
    
    # Find the value at the floor position (lower bound)
    lower_bound_value = sorted_times[math.floor(position) - 1]['responsetime']
    
    # Find the value at the ceil position (upper bound), handle index out of range
    upper_bound_value = sorted_times[math.ceil(position) - 1]['responsetime'] if math.ceil(position) < num_responses else lower_bound_value
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
        response_time_dict_list = []
        last_Error_Occurred_timestamp = None

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
            for metric in apiMetrices:
                if metric.firstByteTime and metric.requestStartTime:
                    timeGap = (metric.firstByteTime-metric.requestStartTime)
                    first_byte_time.append(timeGap)
 
        if query_name in ['response_time', 'percentile_50', 'percentile_90', 'percentile_99']:
            for apiMetric in apiMetrices:
                response_time_dict_list.append({'timestamp': apiMetric.timestamp, 'responsetime': round(float(apiMetric.responseTime), 3), 'success' : apiMetric.success}) 
       
        if query_name == 'last_Error_Occurred':
            last_Error_Occurred = apiMetrices.filter(success=False).last()
            if last_Error_Occurred:
                last_Error_Occurred_timestamp = last_Error_Occurred.timestamp

        # Percentile calculations
        if query_name in ['percentile_50', 'percentile_90', 'percentile_99']:
            percentile_value = int(query_name.split('_')[1])
            currentPercentile = calculatePercentile(percentile_value, response_time_dict_list)
            new_response_time_list = response_time_dict_list if len(response_time_dict_list) == 1 else response_time_dict_list[:-1]
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
            'avg_first_byte_time': round(sum(first_byte_time,timedelta(0)).total_seconds() / len(first_byte_time), 2) if len(first_byte_time)>0 else 0,
            'response_time': response_time_dict_list,
            'percentile_50': {'curr_percentile_res_time': round(float(str(currentPercentile)), 3), 'percentage_diff': round(float(str(percentageDiff)),3)} if query_name == 'percentile_50' else None,
            'percentile_90': {'curr_percentile_res_time': round(float(str(currentPercentile)), 3), 'percentage_diff': round(float(str(percentageDiff)),3)} if query_name == 'percentile_90' else None,
            'percentile_99': {'curr_percentile_res_time': round(float(str(currentPercentile)), 3), 'percentage_diff': round(float(str(percentageDiff)),3)} if query_name == 'percentile_99' else None,
            'last_Error_Occurred':last_Error_Occurred_timestamp
        }
 
    except GraphQLError as gql_error:
        raise gql_error
    except Exception as e:
        raise GraphQLError(f"Unknown error occurred!")

def resolve_metrics(self, info):
    try:
        if not hasattr(self, '_cached_filtered_metrics'):
            timestamp_hours_before = None
            latest_timestamp = None

            filtered_metrics = APIMetrics.objects.filter(api=self).order_by('timestamp')
            query_conditions = Q()

            if filtered_metrics.exists():
                if hasattr(info.context, 'timeRange') and hasattr(info.context, 'timeUnit'):
                    latest_timestamp = filtered_metrics.last().timestamp
                    if latest_timestamp:
                        delta = timedelta(
                            days=30 * info.context.timeRange) if info.context.timeUnit == 'months' else timedelta(
                            hours=info.context.timeRange)
                        timestamp_hours_before = latest_timestamp - delta


                if hasattr(info.context , 'from_date') and info.context.from_date:
                  query_conditions &=  Q(timestamp__gte=info.context.from_date)

                if hasattr(info.context , 'to_date') and info.context.to_date:
                  query_conditions &=  Q(timestamp__lte=info.context.to_date)

                if not hasattr(info.context , 'from_date') and not hasattr(info.context , 'to_date') :
                  if timestamp_hours_before:
                    query_conditions &=  Q(timestamp__gte=timestamp_hours_before)

                  if latest_timestamp:
                     query_conditions &=  Q(timestamp__lte=latest_timestamp)


                filtered_metrics = filtered_metrics.filter( query_conditions )

                self._cached_filtered_metrics = filtered_metrics.filter(query_conditions)
            else:
              raise ObjectDoesNotExist("Object does not exist!")

        return calculateMetrices(self._cached_filtered_metrics, info.field_name)
    except Exception as e:
        pass

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
            html_content = render_to_string('notification_email.html', context)
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
  return MonitoredAPI.objects.select_related('businessUnit', 'subBusinessUnit',).get(pk=serviceId)

def get_metrices(metriceId):
    return APIMetrics.objects.select_related('api').get(pk=metriceId)

def get_assertions_for_service(serviceId):
    assertions = AssertionAndLimit.objects.filter(api__id=serviceId)   
    return assertions


def PrepareContext(apiMetrices, apiName, apiUrl, APIMonitorId=None,errorMessage = None):
    # for record in apiMetrices.values():
    #    print(record)

    return {
        'apiName':apiName,
        'apiUrl':apiUrl,
        'errorMessage': apiMetrices.values_list('errorMessage', flat=True).first() or ['No errors found'],
        'availability_uptime': calculateMetrices(apiMetrices, 'availability_uptime')['availability_uptime'],
        'success_count': calculateMetrices(apiMetrices, 'success_count')['success_count'],
        'avg_latency': calculateMetrices(apiMetrices, 'avg_latency')['avg_latency'],
        'throughput': calculateMetrices(apiMetrices, 'throughput')['throughput'],
        'success_rates': calculateMetrices(apiMetrices, 'success_rates')['success_rates'],
        'error_rates': calculateMetrices(apiMetrices, 'error_rates')['error_rates'],
        'response_time': calculateMetrices(apiMetrices, 'response_time')['response_time'], 
        'percentile_50': calculateMetrices(apiMetrices, 'percentile_50')['percentile_50'], 
        'percentile_90': calculateMetrices(apiMetrices, 'percentile_90')['percentile_90'],
        'percentile_99': calculateMetrices(apiMetrices, 'percentile_99')['percentile_99'],
        'downtime': calculateMetrices(apiMetrices, 'downtime')['downtime'],
        'APIMonitorId': APIMonitorId
    }

def send_email(service, context, cc_email):
    subject = "API Monitoring Task Failed"
    from_email = settings.EMAIL_HOST_USER
    to_email = [] #'rjnsaurabh143@gmail.com', 'rumartime02@gmail.com'


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
        print("sending email first then on teams") 
        email.send(fail_silently=False)

    except (smtplib.SMTPAuthenticationError, smtplib.SMTPRecipientsRefused, 
            smtplib.SMTPSenderRefused, smtplib.SMTPDataError, 
            smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, 
            TimeoutError) as e:
        print(f"SMTP Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred while sending email: {str(e)}")
   
def SendNotificationOnTeams(teamsChannelWebhookURL,context):
    try:
        adaptiveCardJson = {
    
    "type": "message",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "🚨 API Monitoring Alert 🚨",
                        "weight": "Bolder",
                        "size": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": "The following API has encountered issues:",
                        "wrap": "True"
                    },
                    {
                        "type": "TextBlock",
                        "text": f"🔍 **API Name:** {context['apiName']}",
                        "wrap": "True",
                        "weight": "Bolder",
                        "size": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": "🌐 **URL:**",
                        "wrap": "True"
                    },
                    {
                        "type": "TextBlock",
                        "text": f"[{context['apiUrl']}]({context['apiUrl']})",
                        "wrap": "True",
                        "color": "Accent"
                    },
                    {
                        "type": "TextBlock",
                        "text": f"💢 **Error :** {context['errorMessage']}",
                        "wrap": "True",
                        "weight": "Bolder",
                        "size": "Large"
                    },
                    
                    {
                        "type": "TextBlock",
                        "text": "📊 **Metrics Overview:**",
                        "weight": "Bolder",
                        "size": "Medium"
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                            {
                                "type": "Column",
                                "width": "auto",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": "📌 **Metric**",
                                        "weight": "Bolder"
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": "❌ Error Rate"
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": "✅ Success Rate"
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": "⏱️ Average Latency"
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": "🚀 Throughput"
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": "📈 Availability"
                                    }
                                ]
                            },
                            {
                                "type": "Column",
                                "width": "auto",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": "📊 **Value**",
                                        "weight": "Bolder"
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text":  f"{context['error_rates']}%" 
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text":  f"{context['success_rates']}%" 
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{context['avg_latency']} ms" 
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{context['throughput']}" 
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text":  f"{context['availability_uptime']}" 
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "TextBlock",
                        "text": "🌐 **Dashboard URL: **",
                        "wrap": "True"
                    },
                    {
                        "type": "TextBlock",
                        "text": f"http://localhost:3000/api-details/{ context['APIMonitorId'] }",
                        "wrap": "True",
                        "color": "Accent"
                    },
                    {
                        "type": "TextBlock",
                        "text": "📢 Please take the necessary actions to resolve the issue.",
                        "wrap": "True",
                        "weight": "Bolder",
                        "spacing": "Medium"
                    }
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.0"
            }
        }
    ]
}


        headers = {
            'Content-Type':'application/json'
        }
        response = requests.post(teamsChannelWebhookURL, headers=headers, data = json.dumps(adaptiveCardJson))
        response.raise_for_status()
    except Exception as e:
        print(f"error sending notification on team: {e}")    

def UpdateTask(taskId, enabled = True, min = None):
    try:

        periodicTask = PeriodicTask.objects.get(pk = taskId)
        if min is not None:
          crontab = CrontabSchedule.objects.get(id = periodicTask.crontab_id)
          crontab.minute = f'*/{min}'
          crontab.save()

        periodicTask.enabled = enabled
        periodicTask.save()  

        return 'saved'
    except CrontabSchedule.DoesNotExist as cdne:
        raise "Schedule does not exist"    
    except PeriodicTask.DoesNotExist as dne:
        raise "Task does not exist" 
    except Exception as e:
       raise "unknown error occurred"

def CreatePeriodicTask(apiName, min, serviceId):
    try:
        schedule_qs = CrontabSchedule.objects.filter(minute=f'*/{min}')
        if schedule_qs.exists():
            schedule = schedule_qs.first()  # Or handle multiple results
        else:
            schedule = CrontabSchedule.objects.create(minute=f'*/{min}')
        new_task = PeriodicTask.objects.create(
            name=f'my_periodic_task_{apiName}',
            task='ApiMonitoring.tasks.periodicMonitoring',
            crontab=schedule,
            args=json.dumps([f'{serviceId}']), 
            enabled=True
        )
        return new_task
    except Exception as e: 
        print("inside createTask method ",e)