import graphene
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from ApiMonitoring.hitApi import hit_api
from .types import methodTypeChoice, ApiMetricesType, validateApiResponse, MoniterApiType
from graphql import GraphQLError
import json
from django.db.models import Q
from ApiMonitoring.Model.ApiMonitoringModel.graphQl.helpers import get_service

class Query(graphene.ObjectType):
    method_type_choices = graphene.List(methodTypeChoice)

    validate_api = graphene.Field(
        validateApiResponse, 
        apiUrl = graphene.String(required=True),
        methodType = graphene.String(required = True), 
        requestBody = graphene.String(),
        headers = graphene.String()
    )

    get_all_metrices = graphene.List(
        ApiMetricesType, 
        businessUnit = graphene.UUID(), 
        subBusinessUnit = graphene.UUID(),
        apiMonitoringId = graphene.UUID(), 
        from_date = graphene.DateTime(), 
        to_date = graphene.DateTime(),
        searchParam = graphene.String(),
        
        )
    
    get_service_by_id = graphene.Field(
       MoniterApiType,
       serviceId = graphene.UUID(required=True)
    )

    def resolve_method_type_choices(self, info, **kwargs): 
        choices = MonitoredAPI.METHOD_TYPE_CHOICES
        return  [ {'key': key, 'value': value} for key, value in choices]
     

    def resolve_validate_api(self, info, apiUrl, methodType, requestBody=None, headers=None):
        try:
            result = None
          
            if methodType.upper() in ['GET', 'POST']:
                if headers:
                    headers = json.loads(headers)  

                result = hit_api(apiUrl, methodType, headers, requestBody)    
            else:
                raise GraphQLError("Unsupported Method type. Use 'GET' or 'POST'.")
               
            return validateApiResponse(status = result['status'], success = result['success'], message = result['error_message'])
          
        except json.JSONDecodeError as e:
          raise GraphQLError(f"Invalid Header format:")                        
        except Exception as e:
          raise GraphQLError(f"{str(e)}")
        
    def resolve_get_all_metrices(self, info, businessUnit = None, subBusinessUnit = None, apiMonitoringId = None, from_date = None, to_date= None, searchParam = ""):
        try:
            monitoredApiResponse = None 
            query_conditions = Q()

            info.context.from_date = from_date
            info.context.to_date = to_date

            if apiMonitoringId:  
              monitoredApiResponse = MonitoredAPI.objects.filter(id=apiMonitoringId)
              from_date = None
              to_date = None

            elif businessUnit and subBusinessUnit:
              monitoredApiResponse = MonitoredAPI.objects.filter(businessUnit=businessUnit, subBusinessUnit=subBusinessUnit)
            else:
                raise GraphQLError("Please provide either the apiMonitoringId or both businessUnit and subBusinessUnit.")

            if monitoredApiResponse.exists():
                if from_date: 
                  query_conditions &=  Q(createdAt__gte=from_date)
                if to_date:
                  query_conditions &=  Q(createdAt__lte = to_date)
                
                query_conditions &= (Q(apiName__icontains=searchParam) | Q(apiUrl__icontains=searchParam))

                monitoredApiResponse = monitoredApiResponse.filter( query_conditions )   

            else:
                raise GraphQLError("No any api is set to monitored ever") 
  
            return monitoredApiResponse

        except Exception as e:
          raise GraphQLError(f"{str(e)}")  

    def resolve_get_service_by_id(self, info, serviceId):
       try:
          monitoredApi = get_service(serviceId)
          return monitoredApi
       except MonitoredAPI.DoesNotExist:
            raise GraphQLError("Service Not Found!")
       except Exception as e:
          raise GraphQLError(f"{str(e)}")  
          
       
         




