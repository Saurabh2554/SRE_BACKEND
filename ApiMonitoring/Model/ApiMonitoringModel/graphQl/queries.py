import graphene
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI 
from  ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
from ApiMonitoring.hitApi import hit_api
from graphql import GraphQLError
import json
from graphene_django import DjangoObjectType


def calculateMetrices(apiMetrices, query_name):
    #extracting data---
    try:
        total_no_of_requests = apiMetrices.count() 

        if total_no_of_requests ==0:
            raise GraphQLError("No metrics exist for the given API.")

        if query_name == 'availability_uptime':
          total_uptime_requests = apiMetrices.filter(statusCode_gte =200, statusCode_lt= 400).count()


        if query_name =='success_count' or query_name == 'success_rates':
          total_successful_requests = apiMetrices.filter(statusCode=200).count()

        if query_name =='error_count' or query_name == 'error_rates':
          total_failed_requests = apiMetrices.filter(statusCode_gte =400, statusCode_lt= 600).count()
        

        if query_name == 'throughput' or query_name == 'downtime': 
          timestamps = [metric.timestamp for metric in apiMetrices]
          oldest_timestamps = min(timestamps)
          recent_timestamps = max(timestamps)  
          time_difference = (recent_timestamps - oldest_timestamps)

        if query_name == 'avg_latency':
          latency_per_metrices = [(metric.firstByteTime - metric.requestStartTime) for metric in apiMetrices]

        if query_name == 'avg_response_size':
          response_size_per_metrices = [metric.responseSize for metric in apiMetrices]

        if query_name == 'avg_first_byte_time':
          first_byte_time = [metric.firstByteTime for metric in apiMetrices]

        if query_name == 'response_time':
          response_time = [metric.responseTime for metric in apiMetrices]

        #calculating and returning metrices---
        return {
            'availability_uptime':round((total_uptime_requests / total_no_of_requests)*100, 2),
            'success_rates' : round((  total_successful_requests/total_no_of_requests)*100, 2),
            'error_rates' :  round((total_failed_requests/total_no_of_requests)*100, 2),
            'throughput' : round((total_no_of_requests/ (time_difference/ 60.0)), 3),  # request per min
            'avg_latency' : round(sum(latency_per_metrices)/len(latency_per_metrices), 2) if len(latency_per_metrices)>0 else 0 ,
            'downtime' : round(time_difference * ((100 - round((total_uptime_requests / total_no_of_requests)*100, 2))/100), 2) if availability_uptime<100 else 0,
            'success_count' :   total_successful_requests,
            'error_count' : total_failed_requests,
            'avg_response_size' : round(sum(response_size_per_metrices)/len(response_size_per_metrices) , 2) if len (response_size_per_metrices) >0 else 0,
            'avg_first_byte_time' : round(sum(first_byte_time)/len(first_byte_time) , 2) if len (first_byte_time) >0 else 0,
            'response_time': response_time
        }
    except GraphQLError as gql_error:
        raise gql_error  
    except Exception as e:
        raise GraphQLError(f"An error occurred while calculating metrics: {str(e)}")

class ApiMetricesType(DjangoObjectType):
    class Meta:
        model = MonitoredAPI
        fields = ('id', 'apiName','apiType', 'apiUrl','expectedResponseTime')

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
    response_time = graphene.List(graphene.Float())  


    def resolve_metrics(self, info):
        metrics = calculateMetrices(APIMetrics.objects.filter(api=self), info.field_name)
        return metrics

    def resolve_availability_uptime(self, info):
        return self.resolve_metrics(info)['availability_uptime']

    def resolve_success_rates(self, info):
        return self.resolve_metrics(info)['success_rates']

    def resolve_error_rates(self, info):
        return self.resolve_metrics(info)['error_rates']    

    def resolve_throughput(self, info):
        return self.resolve_metrics(info)['throughput']
    
    def resolve_avg_latency(self, info):
        return self.resolve_metrics(info)['avg_latency']

    def resolve_downtime(self, info):
        return self.resolve_metrics(info)['downtime']

    def resolve_success_count(self, info):
        return self.resolve_metrics(info)['success_count']   

    def resolve_error_count(self, info):
        return self.resolve_metrics(info)['error_count']   

    def resolve_avg_response_size(self, info):
        return self.resolve_metrics(info)['avg_response_size'] 

    def resolve_avg_first_byte_time(self, info):
        return self.resolve_metrics(info)['avg_first_byte_time'] 

    def resolve_response_time(self, info):
        return self.resolve_metrics(info)['response_time']      


class apiTypeChoice(graphene.ObjectType):
    key = graphene.String()  
    value = graphene.String()

class validateApiResponse(graphene.ObjectType):
    status = graphene.Int() 
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
        return  [ {'key': key, 'value': value} for key, value in choices]
     

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

            return validateApiResponse(status = result['status'], success = result['success'])    

        except Exception as e:
          raise GraphQLError(f"{str(e)}")
        
    def resolve_get_all_metrices(self, info, businessUnit, subBusinessUnit, apiMonitoringId = None, from_date = None, to_date= None):
        try:
            monitoredApiResponse = None 

            if apiMonitoringId:
              monitoredApiResponse = MonitoredAPI.filter(id=apiMonitoringId)
            elif businessUnit and subBusinessUnit:
              monitoredApiResponse = ApiMonitorModel.objects.filter(businessUnit=businessUnit, subBusinessUnit=subBusinessUnit)
            else:
                raise GraphQLError("You must provide either apiMonitoringId or both businessUnit and subBusinessUnit.")

            if from_date and to_date:
              monitoredApiResponse = monitoredApiResponse.filter(APIMetrics__timestamp__range=(from_date, to_date))

            if monitoredApiResponse.exists():
                return monitoredApiResponse  
            else:
                raise GraphQLError("No any api is set to monitored ever")  

        except Exception as e:
          raise GraphQLError(f"{str(e)}")    




