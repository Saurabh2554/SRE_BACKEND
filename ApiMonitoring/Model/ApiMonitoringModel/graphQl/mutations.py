

import graphene
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
    'isApiActive':True,
    }

    return monitored_api_data

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

            if existingMonitorAPIs is not None :
                raise GraphQLError("Service with the same name already exist!")

            if hasattr(input,'headers') and input.headers:
                input.headers = json.loads(input.headers)

            monitorApiInput = CreateMonitorInput(businessUnit, subbusinessUnit, input)

            with transaction.atomic():
                newMonitoredApi = MonitoredAPI.objects.create(**monitorApiInput)

                input.assertionAndLimit['api'] = newMonitoredApi
                input.schedulingAndAlerting['api'] = newMonitoredApi

                AssertionAndLimit.objects.create(**input.assertionAndLimit)
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
                    

                if input.assertionAndLimit:
                    if input.assertionAndLimit.degradedResponseTime:
                        assertionAndLimit.degradedResponseTime = input.assertionAndLimit.degradedResponseTime

                    if input.assertionAndLimit.failedResponseTime:
                        assertionAndLimit.failedResponseTime = input.assertionAndLimit.failedResponseTime

                    assertionAndLimit.save()

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
        except Exception as e:
            raise GraphQLError(f"Error updating API: {str(e)}")

