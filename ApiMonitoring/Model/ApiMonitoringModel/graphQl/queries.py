import graphene
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from ApiMonitoring.hitApi import hit_api
from .types import apiTypeChoice, ApiMetricesType, validateApiResponse, MoniterApiType
from graphql import GraphQLError
import json

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
        ApiMetricesType, 
        businessUnit = graphene.UUID(), 
        subBusinessUnit = graphene.UUID(),
        apiMonitoringId = graphene.UUID(), 
        from_date = graphene.DateTime(), 
        to_date = graphene.DateTime(),
        )
    
    get_service_by_id = graphene.Field(
       MoniterApiType,
       serviceId = graphene.UUID(required=True)
    )

    def resolve_api_type_choices(self, info, **kwargs): 
        choices = MonitoredAPI.API_TYPE_CHOICES
        return  [ {'key': key, 'value': value} for key, value in choices]
     

    def resolve_validate_api(self, info, apiUrl, apiType, query=None, headers=None):
        try:
            result = None
            if apiType == 'REST':

                headers_dict = headers if headers else {}
                result =  hit_api(apiUrl, apiType, headers_dict) 

            elif apiType == 'GraphQL' :
                if query is None:
                    raise GraphQLError("Query field is required if your api type is GraphQl")

                payload = {
                    'query': query
                }
                
                result = hit_api(apiUrl, apiType, headers, payload)

            return validateApiResponse(status = result['status'], success = result['success'])    

        except Exception as e:
          raise GraphQLError(f"{str(e)}")
        
    def resolve_get_all_metrices(self, info, businessUnit = None, subBusinessUnit = None, apiMonitoringId = None, from_date = None, to_date= None):
        try:
            monitoredApiResponse = None 
            info.context.from_date = from_date
            info.context.to_date = to_date

            if apiMonitoringId:  
              monitoredApiResponse = MonitoredAPI.objects.filter(id=apiMonitoringId)
              info.context.from_date = from_date
              info.context.to_date = to_date

            elif businessUnit and subBusinessUnit:
              monitoredApiResponse = MonitoredAPI.objects.filter(businessUnit=businessUnit, subBusinessUnit=subBusinessUnit)
            else:
                raise GraphQLError("Please provide either the apiMonitoringId or both businessUnit and subBusinessUnit.")
            

            if from_date: 
                monitoredApiResponse = monitoredApiResponse.filter(createdAt__gte=from_date)
            if to_date:
                monitoredApiResponse = monitoredApiResponse.filter(createdAt__lte = to_date)   
              

            if monitoredApiResponse.exists():
                return monitoredApiResponse
            else:
                raise GraphQLError("No any api is set to monitored ever")  

        except Exception as e:
          raise GraphQLError(f"{str(e)}")  

    def resolve_get_service_by_id(self,info,serviceId):
       try:
          monitoredApi = MonitoredAPI.objects.get(pk=serviceId)
          return monitoredApi
       except MonitoredAPI.DoesNotExist:
            raise GraphQLError("Service Not Found!")
       except Exception as e:
          raise GraphQLError(f"{str(e)}")  
          
       
         




