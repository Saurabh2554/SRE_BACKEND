import graphene
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI 
from  ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
from ApiMonitoring.hitApi import hit_api
from graphql import GraphQLError
import json


def calculateMetrices(apiMetrices):
    #extracting data---
    total_no_of_requests = apiMetrices.count()
    total_uptime_requests = apiMetrices.filter(statusCode_gte =200, statusCode_lt= 400).count()
    total_successful_requests = apiMetrices.filter(statusCode=200).count()
    total_failed_requests = apiMetrices.filter(statusCode_gte =400, statusCode_lt= 600).count()
    timestamps = [metric.timestamp for metric in apiMetrices]
    oldest_timestamps = min(timestamps)
    recent_timestamps = max(timestamps)
    time_difference = (recent_timestamps - oldest_timestamps)
    latency_per_metrices = [(metric.firstByteTime - metric.requestStartTime) for metric in apiMetrices]
    response_size_per_metrices = [metric.responseSize for metric in apiMetrices]
    first_byte_time = [metric.firstByteTime for metric in apiMetrices]

    #calculating and returning metrices---
    return {
        'availability_uptime':round((total_uptime_requests / total_no_of_requests)*100, 2),
        'success_rates' : round((total_successful_requests/total_no_of_requests)*100, 2),
        'error_rates' :  round((total_failed_requests/total_no_of_requests)*100, 2),
        'throughput' : round((total_no_of_requests/ (time_difference/ 60.0)), 3),  # request per min
        'avg_latency' : round(sum(latency_per_metrices)/len(latency_per_metrices), 2) if len(latency_per_metrices)>0 else 0 ,
        'downtime' : round(time_difference * ((100 - availability_uptime)/100), 2),
        'success_count' : total_successful_requests,
        'error_count' : total_failed_requests,
        'avg_response_size' : round(sum(response_size_per_metrices)/len(response_size_per_metrices) , 2) if len (response_size_per_metrices) >0 else 0,
        'avg_first_byte_time' : round(sum(first_byte_time)/len(first_byte_time) , 2) if len (first_byte_time) >0 else 0,
    }
    


class apiTypeChoice(graphene.ObjectType):
    key = graphene.String()  
    value = graphene.String()

class validateApiResponse(graphene.ObjectType):
    status = graphene.Int() 
    response_time = graphene.Float()
    success = graphene.Boolean()

class apiMetricesResponse(graphene.ObjectType):
      availability_uptime = graphene.Float()
      success_rates = graphene.Float()
      error_rates = graphene.Float()
      throughput = graphene.Float()
      avg_latency =graphene.Float() 
      downtime = graphene.Float()
      success_count = graphene.Int()
      error_count = graphene.Int()
      avg_response_size = graphene.Float()
      avg_first_byte_time = graphene.Float()


class Query(graphene.ObjectType):
    api_type_choices = graphene.List(apiTypeChoice)

    validate_api = graphene.Field(
        validateApiResponse, 
        apiUrl = graphene.String(required=True),
        apiType = graphene.String(required = True), 
        query = graphene.String(),
        headers = graphene.String()
    )

    get_all_metrices = graphene.List(
        apiMetricesResponse, 
        businessUnit = graphene.UUID(required = True), 
        subBusinessUnit = graphene.UUID(required = True),
        apiMonitoringId = graphene.UUID(), 
        from_date = graphene.DateTime(), 
        to_date = graphene.DateTime(),
        )
    


    def resolve_api_type_choices(self, info, **kwargs): 
        choices = MonitoredAPI.API_TYPE_CHOICES
        return [
            {'key': key, 'value': value} for key, value in choices
        ]

    def resolve_validate_api(self, info, apiUrl, apiType, query=None, headers=None):
        try:
            result = None
            if apiType == 'REST':

                headers_dict = json.loads(headers) if headers else {}
                result =  hit_api(apiUrl, apiType, headers_dict) 

            elif apiType == 'GraphQL' :
                if query is None:
                    raise GraphQLError("Query field is required if youur api type is GraphQl")
                payload = {
                    'query': query
                }
                
                result = hit_api(apiUrl, apiType, headers, payload)

            return validateApiResponse(status = result['status'], response_time = result['response_time'], success = result['success'])    

        except Exception as e:
          raise GraphQLError(f"{str(e)}")
        
    def resolve_get_all_metrices(self, info, businessUnit, subBusinessUnit, apiMonitoringId = None, from_date = None, to_date= None):
        try:
            apiMetrices = None
            monitoredApiResponse = None

            if apiMonitoringId is not None:
                monitoredApiResponse = MonitoredAPI.objects.get(
                 pk = monitoredApiId
                )
            else :    
               monitoredApiResponse = MonitoredAPI.objects.get(
                 businessUnit= businessUnit,
                 subBusinessUnit= subBusinessUnit
                )
            
            if monitoredApiResponse is not None:
                apiMetrices = APIMetrics.objects.filter(api = monitoredApiResponse.id) 
                
                if apiMetrices is not None:
                    if from_date is not None:
                        apiMetrices = apiMetrices.filter(timestamp_gte = from_date)

                    if to_date is not None:
                        apiMetrices = apiMetrices.filter(timestamp_lte = to_date)  

                    result = calculateMetrices(apiMetrices)
                    return apiMetricesResponse(**result)
                else:
                    raise GraphQLError("No any api is set to monitored ever")  

            else:
                raise GraphQLError("Either business unit or sub business unit does not exist")
        except Exception as e:
          raise GraphQLError(f"{str(e)}")    




