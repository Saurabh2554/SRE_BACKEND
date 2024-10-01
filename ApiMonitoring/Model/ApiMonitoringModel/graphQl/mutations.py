import graphene
from .types import MoniterApiType 
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI 
from  ApiMonitoring.Model.ApiConfigModel.restApiConfigModels import RestAPIConfig
from  ApiMonitoring.Model.ApiConfigModel.graphQlApiConfigModels import GraphQLAPIConfig
from  Business.models import BusinessUnit , SubBusinessUnit
from ApiMonitoring.Model.AuthTypeModel.authConfigModels import Authentication
from graphql import GraphQLError
from ApiMonitoring.tasks import monitorApi


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


# Monitor a new Api
class ApiMonitorCreateMutation(graphene.Mutation):
            class Arguments:
                input = MonitoredApiInput(required = True)
            
            monitoredApi = graphene.Field(MoniterApiType) 
            success = graphene.Boolean()
            message = graphene.String()


            def mutate(self, info, input):
             try:
                graphQlApiConfig = None
                restApiConfig = None
                headers = {}

                # authentication = Authentication.objects.get(pk=input.authentication)
                

                existingMonitorAPIs = MonitoredAPI.objects.filter(
                    apiUrl__iexact=f'{input.apiUrl}',
                    apiType=input.apiType
                    ).first()
                
                businessUnit = BusinessUnit.objects.get(pk = input.businessUnit)
                subBusinessUnit = SubBusinessUnit.objects.get(pk = input.subBusinessUnit)
            
                
                if existingMonitorAPIs is not None:
                    if not existingMonitorAPIs.isApiActive:
                        # Reactive the paused API
                        existingMonitorAPIs.isApiActive = True
                        existingMonitorAPIs.save()
                        return ApiMonitorUpdateMutation().mutate(info, id=existingMonitorAPIs.id, input=input)
                    else: 
                        raise GraphQLError("Same service already being monitored")
                        
                if input.headers is not None:
                    for key , value in enumerate(input.headers, start=1):
                        headers['key'] = value


                if input.apiType == 'REST':
                    restApiConfig = RestAPIConfig.objects.create(
                        method = input.apiType,
                    )

                if input.apiType == 'GraphQL':
                    graphQlApiConfig = GraphQLAPIConfig.objects.create(
                    graphql_query = input.graphqlQuery     
                    )    

                newMonitoredApi = MonitoredAPI.objects.create(
                businessUnit=businessUnit, 
                subBusinessUnit = subBusinessUnit,
                apiName = input.apiName,
                apiType = input.apiType,
                apiUrl = input.apiUrl, 
                apiCallInterval = input.apiCallInterval, 
                expectedResponseTime = input.expectedResponseTime,  
                headers = headers, 
                # authentication = authentication
                restApiConfig = restApiConfig,
                graphqlApiconfig = graphQlApiConfig,
                recipientDl = input.recipientDl,
                createdBy = input.createdBy,
                lastModifiedBy = input.createdBy
                
                )

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

