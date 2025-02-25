

import graphene
import re
from .types import MoniterApiType, AssertionAndLimitQueryType, SchedulingAndAlertingQueryType
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from  ApiMonitoring.Model.ApiMonitoringModel.assertionAndLimitModels import AssertionAndLimit
from  ApiMonitoring.Model.ApiMonitoringModel.schedulingAndAlertingModels import SchedulingAndAlerting
from  Business.models import BusinessUnit , SubBusinessUnit
from  graphql import GraphQLError
from  ApiMonitoring.tasks import monitorApiTask, revokeTask, periodicMonitoring
from .types import MonitoredApiInput, MonitoredApiUpdateInput
import json
from ApiMonitoring.Model.ApiMonitoringModel.graphQl.helpers import UpdateTask, CreatePeriodicTask, get_service
from django.db import transaction

def ExtractBusinessAndSubBusinessUnit(businessUnitId, subBusinessUnitId):
    try:
        businessUnit = BusinessUnit.objects.get(pk = businessUnitId)
        subBusinessUnit = SubBusinessUnit.objects.get(pk = subBusinessUnitId)
         
        return businessUnit, subBusinessUnit

    except BusinessUnit.DoesNotExist as be:
        raise GraphQLError(f"{be}")
    except SubBusinessUnit.DoesNotExist as sbe:
        raise GraphQLError(f"{sbe}")        
    except Exception as ex:
        raise GraphQLError(f"{ex}")

def CheckExistingApi(input):
  try:
    return MonitoredAPI.objects.filter(
        # apiUrl__iexact=f'{input.apiUrl}',
        # apiType=input.apiType
        apiName__iexact=f'{input.apiName}'
        ).first()

  except Exception as e:
      raise GraphQLError(f"{e}")


def CreateMonitorInput(businessUnit, subBusinessUnit, input):
    monitored_api_data = {
    'businessUnit': businessUnit,
    'subBusinessUnit': subBusinessUnit,
    'apiName': input.apiName,
    'apiUrl': input.apiUrl,
    'headers': input.headers,
    'methodType' : input.methodType,
    'requestBody' : input.requestBody,
    'failedResponseTime' : input.failedResponseTime,
    'degradedResponseTime' : input.degradedResponseTime,
    'isApiActive':True,
    }

    return monitored_api_data

def is_valid_json_path(path):
    try:
        # Regex for JSON path with array index support
        json_path_pattern = r"^\$((\.[a-zA-Z_][a-zA-Z0-9_]*)|(\[['\"].+?['\"]\])|(\[\d+\]))*$"
        
        # Validate path with regex
        if not isinstance(path, str):
            return False
        if re.match(json_path_pattern, path):
            return True
        return False
    except Exception:
        return False



def checkValidAssertion(assertionLimit,newMonitoredApi):
    # replace 
    VALID_OPERATORS = {
        'status_code': ['equals', 'not_equals', 'greater_than', 'less_than'],
        'headers': ['equals', 'not_equals', 'is_empty', 'is_not_empty', 'greater_than', 'less_than', 'contains', 'not_contains'],
        'json_body': ['equals', 'not_equals', 'is_empty', 'is_not_empty', 'greater_than', 'less_than', 'contains', 'not_contains', 'is_null','is_not_null']
    }


    ALLOW_PROPERTY = {
    'headers': True,  
    'json_body': True,  
    'status_code': False
    }

    source = assertionLimit.get('source')
    property_value = assertionLimit.get('property')
    operator = assertionLimit.get('operator')

    existing_assertion = AssertionAndLimit.objects.filter(
                                        api=newMonitoredApi,
                                        source=source,
                                        property=property_value,
                                        operator=operator
                                        ).first()

    if existing_assertion:
         raise GraphQLError(f"An assertion with the same source, property, and operator already exists for this API.")
    

    if source not in VALID_OPERATORS:
        raise GraphQLError(f"Invalid source: {source}. Allowed sources are: {', '.join(VALID_OPERATORS.keys())}.")
    
    if operator not in VALID_OPERATORS[source]:
        raise GraphQLError(f"Invalid operator: {operator} for source: {source}. Allowed operaotrs are: {', '.join(VALID_OPERATORS[source])}.")
    
    if not ALLOW_PROPERTY[source] and property_value :
        raise GraphQLError(f"Property is not allowed for source: {source}. Please remove the property field. ")
    
    if ALLOW_PROPERTY[source] and not property_value:
         raise GraphQLError(f"Property is required for source: {source}. Please provide a valid property.")
    
    if source == 'json_body' and property_value and not is_valid_json_path(property_value):
        raise GraphQLError(f"Invalid property for JSON Body. Only JSON path is allowed, no regex.")
    


# Monitor a new Api
class ApiMonitorCreateMutation(graphene.Mutation):

    class Arguments:
        input = MonitoredApiInput(required = True)
    
    monitoredApi = graphene.Field(MoniterApiType) 
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input):
        try:
            businessUnit, subbusinessUnit = ExtractBusinessAndSubBusinessUnit(input.businessUnit, input.subBusinessUnit)

            existingMonitorAPIs = CheckExistingApi(input = input)

            if input.schedulingAndAlerting and not(hasattr(input.schedulingAndAlerting,'recipientDl') and input.schedulingAndAlerting.recipientDl):
                raise GraphQLError("receipentDL is required in scheduling And Alerting")


            if existingMonitorAPIs is not None :
                raise GraphQLError("Service with the same name already exist!")

            if hasattr(input,'headers') and input.headers:
                input.headers = json.loads(input.headers)

            monitorApiInput = CreateMonitorInput(businessUnit, subbusinessUnit, input)

            with transaction.atomic():
                newMonitoredApi = MonitoredAPI.objects.create(**monitorApiInput)
                
                assertion_limits =[]
                for assertionLimit in input.assertionAndLimit:
                    assertionLimit['api'] = newMonitoredApi

                    checkValidAssertion(assertionLimit,newMonitoredApi)
                    
                    assertion_limits.append(AssertionAndLimit(**assertionLimit))

                
                # input.assertionAndLimit['api'] = newMonitoredApi
                input.schedulingAndAlerting['api'] = newMonitoredApi

                AssertionAndLimit.objects.bulk_create(assertion_limits)
                SchedulingAndAlerting.objects.create(**input.schedulingAndAlerting)

                taskResponse = CreatePeriodicTask(input.apiName, input.schedulingAndAlerting.apiCallInterval, newMonitoredApi.id)

                newMonitoredApi.taskId = taskResponse
                newMonitoredApi.save()

            periodicMonitoring.delay(newMonitoredApi.id)
            return ApiMonitorCreateMutation(monitoredApi = newMonitoredApi, success = True , message = "Api monitoring started")    
       
        except json.JSONDecodeError as e:
          raise GraphQLError(f"Invalid Header format") 
        except Exception as e:
            raise GraphQLError(f"{str(e)}")
                  
                  
class ApiMonitorUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)  
        isApiActive = graphene.Boolean()
        input = MonitoredApiUpdateInput() 

    monitoredApi = graphene.Field(MoniterApiType)
    assertionAndLimit = graphene.Field(AssertionAndLimitQueryType)
    schedulingAndAlerting = graphene.Field(SchedulingAndAlertingQueryType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, isApiActive, input = None):
        try:
            # Fetch the existing MonitoredAPI by its ID
            monitoredApi = get_service(id)
            assertionAndLimit = AssertionAndLimit.objects.get(api=id)
            schedulingAndAlerting = SchedulingAndAlerting.objects.get(api=id)
            message = None

            if input is not None:
                if input.schedulingAndAlerting:
                    if input.schedulingAndAlerting.apiCallInterval:
                        schedulingAndAlerting.apiCallInterval = input.schedulingAndAlerting.apiCallInterval

                    if input.schedulingAndAlerting.maxRetries:
                        schedulingAndAlerting.maxRetries = input.schedulingAndAlerting.maxRetries
                    
                    if input.schedulingAndAlerting.retryAfter:
                        schedulingAndAlerting.retryAfter = input.schedulingAndAlerting.retryAfter

                    if input.schedulingAndAlerting.teamsChannelWebhookURL:
                        schedulingAndAlerting.teamsChannelWebhookURL = input.schedulingAndAlerting.teamsChannelWebhookURL  

                    schedulingAndAlerting.save()
                    

                # if input.assertionAndLimit:
                #     if input.degradedResponseTime:
                #         assertionAndLimit.degradedResponseTime = input.assertionAndLimit.degradedResponseTime

                #     if input.failedResponseTime:
                #         assertionAndLimit.failedResponseTime = input.assertionAndLimit.failedResponseTime

                #     assertionAndLimit.save()

                if input.headers:
                    monitoredApi.headers = input.headers  

            monitoredApi.isApiActive = isApiActive
            if monitoredApi.taskId:
                task_id = monitoredApi.taskId.id
                UpdateTask(task_id, monitoredApi.isApiActive, schedulingAndAlerting.apiCallInterval)
            
            if isApiActive:
                periodicMonitoring.delay(id)
            
            monitoredApi.save()
            
            


            return ApiMonitorUpdateMutation(
                monitoredApi=monitoredApi,
                success=True,
                message= f'Service {"activated" if isApiActive else "deactivated"} ' 
            )

        except MonitoredAPI.DoesNotExist:
            raise GraphQLError("API to be updated not found")
        
        except AssertionAndLimit.DoesNotExist:
            raise GraphQLError("AssertionAndLimit API fields to be updated not found")
        
        except SchedulingAndAlerting.DoesNotExist:
            raise GraphQLError("SchedulingAndAlerting API fields to be updated not found")
        
        except Exception as e:
            raise GraphQLError(f"Error updating API: {str(e)}")

