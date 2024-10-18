import graphene
from .types import MoniterApiType 
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI 
from  ApiMonitoring.Model.ApiConfigModel.restApiConfigModels import RestAPIConfig
from  ApiMonitoring.Model.ApiConfigModel.graphQlApiConfigModels import GraphQLAPIConfig
from  Business.models import BusinessUnit , SubBusinessUnit
# from  ApiMonitoring.Model.AuthTypeModel.authConfigModels import Authentication
from  graphql import GraphQLError
from  ApiMonitoring.tasks import monitorApiTask, revokeTask, periodicMonitoring
from .types import MonitoredApiInput
import json
from django_celery_beat.models import PeriodicTask, CrontabSchedule

def UpdateTask(taskId,enabled = True, min = None, ):
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
        schedule, created = CrontabSchedule.objects.get_or_create(minute=f'*/{min}')  
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

def CreateConfiguration(input):
    try:
        api_config_mapping = {
            'REST': lambda: RestAPIConfig.objects.create(method=input.apiType),
            'GraphQL': lambda: GraphQLAPIConfig.objects.create(graphql_query=input.graphqlQuery)
        }

        if input.apiType not in api_config_mapping:
            raise GraphQLError("Unsupported API Type.")

        api_config = api_config_mapping[input.apiType]()

        return {
            'restApiConfig': api_config if input.apiType == 'REST' else None,
            'graphQlApiConfig': api_config if input.apiType == 'GraphQL' else None
        }   
    except Exception as e:
        raise GraphQLError(f"{e}")    
    
def CreateMonitorInput(businessUnit, subBusinessUnit, headers, apiConfig, input):
    monitored_api_data = {
    'businessUnit': businessUnit,
    'subBusinessUnit': subBusinessUnit,
    'apiName': input.apiName,
    'apiType': input.apiType,
    'apiUrl': input.apiUrl,
    'apiCallInterval': input.apiCallInterval,
    'expectedResponseTime': input.expectedResponseTime,
    'headers': headers,
    'restApiConfig': apiConfig['restApiConfig'],
    'graphqlApiconfig': apiConfig['graphQlApiConfig'],
    'recipientDl': input.recipientDl,
    'createdBy': input.createdBy,
    'isApiActive':True
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
                    
            apiConfig = CreateConfiguration(input) 

            monitorApiInput = CreateMonitorInput(businessUnit, subbusinessUnit, input.headers, apiConfig, input)
            
            newMonitoredApi = MonitoredAPI.objects.create(**monitorApiInput)
            taskResponse = CreatePeriodicTask(input.apiName, input.apiCallInterval, newMonitoredApi.id)
            newMonitoredApi.taskId = taskResponse
            newMonitoredApi.save()
            periodicMonitoring.delay(MonitoredAPI.id)

            return ApiMonitorCreateMutation(monitoredApi = newMonitoredApi, success = True , message = "Api monitoring started")    
        except Exception as e:
            raise GraphQLError(f"{str(e)}")
                  
                  
class ApiMonitorUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)  
        isApiActive = graphene.Boolean()
        input = MonitoredApiInput() 

    monitoredApi = graphene.Field(MoniterApiType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, isApiActive, input = None):
        try:
            # Fetch the existing MonitoredAPI by its ID
            monitoredApi = MonitoredAPI.objects.get(pk=id)
            message = None

            if input is not None:
                if input.apiCallInterval:
                    monitoredApi.apiCallInterval = input.apiCallInterval

                if input.expectedResponseTime:
                    monitoredApi.expectedResponseTime = input.expectedresponseTime

                if input.headers:
                    monitoredApi.headers = input.headers  


            monitoredApi.isApiActive = isApiActive
            UpdateTask(monitoredApi.taskId, monitoredApi.isApiActive, monitoredApi.apiCallInterval)

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

