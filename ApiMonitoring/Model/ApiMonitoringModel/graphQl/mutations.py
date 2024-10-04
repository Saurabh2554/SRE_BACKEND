import graphene
from .types import MoniterApiType 
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI 
from  ApiMonitoring.Model.ApiConfigModel.restApiConfigModels import RestAPIConfig
from  ApiMonitoring.Model.ApiConfigModel.graphQlApiConfigModels import GraphQLAPIConfig
from  Business.models import BusinessUnit , SubBusinessUnit
from  ApiMonitoring.Model.AuthTypeModel.authConfigModels import Authentication
from  graphql import GraphQLError
from  ApiMonitoring.tasks import monitorApi


#Monitored  Api input values
class MonitoredApiInput(graphene.InputObjectType):
    businessUnit = graphene.UUID(required = True)
    subBusinessUnit = graphene.UUID(required = True)
    apiName = graphene.String()  
    apiType = graphene.String()  
    apiUrl = graphene.String()  
    apiCallInterval = graphene.Int()  
    expectedResponseTime = graphene.Int()  
    headers = graphene.JSONString() 
    graphqlQuery = graphene.String()
    recipientDl = graphene.String()
    createdBy = graphene.String()
    lastModifiedBy = graphene.String()

def ExtractBusinessAndSubBusinessUnit(self, businessUnitId, subBusinessUnitId):
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

def CheckExistingApi(self, apiObject):
  try:
    return apiObject.objects.filter(
        apiUrl__iexact=f'{input.apiUrl}',
        apiType=input.apiType
        ).first()

  except Exception as e:
      raise GraphQLError(f"{e}")    

def CreateConfiguration(self, apiType):
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
    
def CreateMonitorInput(self, businessUnit, subBusinessUnit, headers, apiConfig, input):
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
    'lastModifiedBy': input.createdBy
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
                headers = {}
                
                existingMonitorAPIs = CheckExistingApi(MonitoredAPI)  
                businessUnit, subbusinessUnit = ExtractBusinessAndSubBusinessUnit(input.businessUnit, input.subBusinessUnit)
            
                if existingMonitorAPIs.exists():
                    if not existingMonitorAPIs.isApiActive:
                        existingMonitorAPIs.isApiActive = True
                        existingMonitorAPIs.save()
                        return ApiMonitorUpdateMutation().mutate(info, id=existingMonitorAPIs.id, input=input)
                    else: 
                        raise GraphQLError("Same service already being monitored")
                        
                if input.headers:
                    for key , value in enumerate(input.headers, start=1):
                        headers['key'] = value

                apiConfig = CreateConfiguration(input.apiType) 

                monitorApiInput = CreateMonitorInput(businessUnit, subbusinessUnit, apiConfig, input)

                newMonitoredApi = MonitoredAPI.objects.create(**monitorApiInput)

                response = monitorApi.delay(input.apiUrl, input.apiType, headers, newMonitoredApi.id)

                return ApiMonitorCreateMutation(monitoredApi = newMonitoredApi, success = True , message = "Api monitoring started")    
             except Exception as e:
                raise GraphQLError(f"{str(e)}")
                  
                  
class ApiMonitorUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)  
        input = MonitoredApiInput(required=False) 

    monitoredApi = graphene.Field(MoniterApiType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, input):
        try:
            # Fetch the existing MonitoredAPI by its ID
            monitoredApi = MonitoredAPI.objects.get(id=id)
            headers = {}
        
            monitoredApi.apiCallInterval = input.apiCallInterval if input.apiCallInterval else monitoredApi.apiCallInterval
            monitoredApi.expectedResponseTime = input.expectedResponseTime if input.expectedResponseTime else monitoredApi.expectedResponseTime
            monitoredApi.lastModifiedBy = input.lastModifiedBy if input.lastModifiedBy else monitoredApi.lastModifiedBy
            # need to add lastmodified by 
            
            
            if input.headers is not None:
                    for key , value in enumerate(input.headers, start=1):
                        headers['key'] = value
                    monitoredApi.headers = headers

            
            monitoredApi.save()

            
            if monitorApi.isApiActive:
                response = monitorApi.delay(monitoredApi.apiUrl, monitoredApi.apiType, headers, monitoredApi.id)

                # need to check response is Monitored then we need to add this return statement 
                # Return a success message

                return ApiMonitorUpdateMutation(
                monitoredApi=monitoredApi,
                success=True,
                message="API monitoring details updated successfully and API monitoring started"
            )
            


            return ApiMonitorUpdateMutation(
                monitoredApi=monitoredApi,
                success=True,
                message="API monitoring details updated successfully"
            )

        except MonitoredAPI.DoesNotExist:
            raise GraphQLError("API to be updated not found")
        except Exception as e:
            raise GraphQLError(f"Error updating API: {str(e)}")

