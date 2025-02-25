import graphene
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from  ApiMonitoring.Model.ApiMonitoringModel.schedulingAndAlertingModels import SchedulingAndAlerting
from  ApiMonitoring.Model.ApiMonitoringModel.assertionAndLimitModels import AssertionAndLimit
from ApiMonitoring.hitApi import hit_api
from .types import methodTypeChoice, ApiMetricesType, validateApiResponse, MoniterApiType,sourceTypeOperatorChoice
from graphql import GraphQLError
import json
from django.db.models import Q
from ApiMonitoring.Model.ApiMonitoringModel.graphQl.helpers import get_service
import requests
from django.db.models import Prefetch


class Query(graphene.ObjectType):
    method_type_choices = graphene.List(methodTypeChoice)

    assertion_source_operator_choices = graphene.Field(
       sourceTypeOperatorChoice,
       source_type=graphene.String(required=True)
       )

    validate_api = graphene.Field(
        validateApiResponse, 
        apiUrl = graphene.String(required=True),
        methodType = graphene.String(required = True), 
        requestBody = graphene.String(),
        headers = graphene.String()
    )
    validate_teams_channel = graphene.Field(
        validateApiResponse,
        channelUrl=graphene.String(required=True),
    )

    get_all_metrices = graphene.List(
        ApiMetricesType, 
        businessUnit = graphene.UUID(), 
        subBusinessUnit = graphene.UUID(),
        apiMonitoringId = graphene.UUID(), 
        from_date = graphene.DateTime(), 
        to_date = graphene.DateTime(),
        searchParam = graphene.String(),
        timeRange = graphene.Int(),
        timeUnit = graphene.String()
        )
    
    get_service_by_id = graphene.Field(
       MoniterApiType,
       serviceId = graphene.UUID(required=True)
    )

    def resolve_method_type_choices(self, info, **kwargs): 
        choices = MonitoredAPI.METHOD_TYPE_CHOICES
        return  [ {'key': key, 'value': value} for key, value in choices]
    
    def resolve_assertion_source_operator_choices(self, info,source_type, **kwargs):
        VALID_OPERATORS = {
        'status_code': ['equals', 'not_equals', 'greater_than', 'less_than'],
        'header': ['equals', 'not_equals', 'is_empty', 'is_not_empty', 'greater_than', 'less_than', 'contains', 'not_contains'],
        'json_body': ['equals', 'not_equals', 'is_empty', 'is_not_empty', 'greater_than', 'less_than', 'contains', 'not_contains', 'is_null','is_not_null']
    }
        
        ALLOW_PROPERTY = {
    'header': True,  
    'json_body': True,  
    'status_code': False
    }

    
        return sourceTypeOperatorChoice(
           source=source_type, 
           propertyVisibility = ALLOW_PROPERTY.get(source_type,False),
           operators=VALID_OPERATORS.get(source_type,[] )
        )
            
        
       
       
    

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
          raise GraphQLError("Invalid Header format:")
        except Exception as e:
          raise GraphQLError(f"{str(e)}")

    def resolve_validate_teams_channel(self, info, channelUrl):
        try:
            response = None

            response = requests.post(channelUrl, json={"text": "Test"})

            if(response.status_code>=400 and response.status_code<500):
                return validateApiResponse(status=response.status_code, success=False,
                                       message='InValid')

            elif(response.status_code>=500):
                return validateApiResponse(status=response.status_code, success=False,
                                           message='Server Error! URL not available')
            else:
                return validateApiResponse(status=response.status_code, success=True,
                                       message='Valid')

        except Exception as e:
            return validateApiResponse(status=400, success=False,
                                       message='InValid')

    def resolve_get_all_metrices(self, info, businessUnit = None, subBusinessUnit = None, apiMonitoringId = None, from_date = None, to_date= None, searchParam = "",timeRange = 12,timeUnit = 'hours'):
        try:
            monitoredApiResponse = None 
            query_conditions = Q()
            
            if apiMonitoringId:  
              monitoredApiResponse = MonitoredAPI.objects.filter(id=apiMonitoringId)
              info.context.timeRange = timeRange
              info.context.timeUnit = timeUnit

            elif businessUnit and subBusinessUnit:
              monitoredApiResponse = MonitoredAPI.objects.filter(businessUnit=businessUnit, subBusinessUnit=subBusinessUnit)
            else:
                raise GraphQLError("Please provide either the apiMonitoringId or both (businessUnit and subBusinessUnit).")

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
          
       
         




