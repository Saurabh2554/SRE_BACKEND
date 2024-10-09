import graphene
from .types import MoniterApiType 
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI 
from  ApiMonitoring.Model.ApiConfigModel.restApiConfigModels import RestAPIConfig
from  ApiMonitoring.Model.ApiConfigModel.graphQlApiConfigModels import GraphQLAPIConfig
from  Business.models import BusinessUnit , SubBusinessUnit
# from  ApiMonitoring.Model.AuthTypeModel.authConfigModels import Authentication
from  graphql import GraphQLError
from  ApiMonitoring.tasks import monitorApi, revokeTask
from .types import MonitoredApiInput
import json

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
        apiUrl__iexact=f'{input.apiUrl}',
        apiType=input.apiType
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
    'createdBy': input.createdBy
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
                    if not existingMonitorAPIs.isApiActive:
                        return ApiMonitorUpdateMutation().mutate(info, id=existingMonitorAPIs.id, isApiActive=True, input=input)
                    else: 
                        raise GraphQLError("Same service already being monitored")
                        
                apiConfig = CreateConfiguration(input) 

                monitorApiInput = CreateMonitorInput(businessUnit, subbusinessUnit, input.headers, apiConfig, input)

                newMonitoredApi = MonitoredAPI.objects.create(**monitorApiInput)

                response = monitorApiTask(input.apiUrl, input.apiType, input.headers, newMonitoredApi.id)

                return ApiMonitorCreateMutation(monitoredApi = newMonitoredApi, success = True , message = "Api monitoring started")    
             except Exception as e:
                raise GraphQLError(f"{str(e)}")
                  
                  
class ApiMonitorUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)  
        isApiActive = graphene.Boolean(required=True)
        input = MonitoredApiInput() 

    monitoredApi = graphene.Field(MoniterApiType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, isApiActive, input = None):
        try:
            # Fetch the existing MonitoredAPI by its ID
            monitoredApi = MonitoredAPI.objects.get(pk=id)
            message = None
        
            monitoredApi.apiCallInterval = input.apiCallInterval if input and input.apiCallInterval else monitoredApi.apiCallInterval
            monitoredApi.expectedResponseTime = input.expectedResponseTime if input and input.expectedResponseTime else monitoredApi.expectedResponseTime
            monitoredApi.headers = input.headers if input and input.headers else monitoredApi.headers

            monitoredApi.isApiActive = isApiActive
         
            if isApiActive:
                response = monitorApiTask(monitoredApi.apiUrl, monitoredApi.apiType, monitoredApi.headers, id)          
                message = "API monitoring details updated successfully and API monitoring started"
            else:
                response = revokeTask(monitoredApi.taskId)
                monitoredApi.taskId = None
                message = "Service Deactivated!"

            monitoredApi.save()

            return ApiMonitorUpdateMutation(
                monitoredApi=monitoredApi,
                success=True,
                message= message 
            )

        except MonitoredAPI.DoesNotExist:
            raise GraphQLError("API to be updated not found")
        except Exception as e:
            raise GraphQLError(f"Error updating API: {str(e)}")

