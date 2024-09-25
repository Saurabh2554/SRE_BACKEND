import graphene
from .types import MoniterApiType 
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI 
from  ApiMonitoring.Model.ApiConfigModel.restApiConfigModels import RestAPIConfig
from  ApiMonitoring.Model.ApiConfigModel.graphQlApiConfigModels import GraphQLAPIConfig
from  Business.models import BusinessUnit , SubBusinessUnit
from ApiMonitoring.Model.AuthTypeModel.authConfigModels import Authentication
from graphql import GraphQLError
# from ApiMonitoring.tasks import add


#Monitored  Api input values
class MonitoredApiInput(graphene.InputObjectType):
    businessUnit = graphene.UUID(required = True)
    subBusinessUnit = graphene.UUID(required = True)
    apiName = graphene.String()  
    apiType = graphene.String()  
    apiUrl = graphene.String()  
    apiCallInterval = graphene.Int()  
    expectedResponseTime = graphene.Int()  
    expectedStatusCode = graphene.Int()
    headers = graphene.JSONString() 
    graphqlQuery = graphene.String()
    # authentication = graphene.UUID(required = True)
    # restApiConfig = graphene.UUID(required = True)
    # graphqlApiconfig = graphene.UUID(required = True)
    recipientDl = graphene.String()
    createdBy = graphene.String()


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

                # authentication = Authentication.objects.get(pk=input.authentication)
                

                existingMonitorAPIs = MonitoredAPI.objects.filter(
                    apiUrl__iexact=f'{input.apiUrl}',
                    apiType=input.apiType
                    ).first()
                
                businessUnit = BusinessUnit.objects.get(pk = input.businessUnit)
                subBusinessUnit = SubBusinessUnit.objects.get(pk = input.subBusinessUnit)
                

                # print(businessUnit,subBusinessUnit,"gggggggggggggggggg")
                
                if existingMonitorAPIs is not None:
                    if not existingMonitorAPIs.isApiActive:
                        # Reactive the paused API
                        existingMonitorAPIs.isApiActive = True
                        existingMonitorAPIs.save()
                        return ApiMonitorCreateMutation(
                            success = True,
                            message = "API monitoring reactivated"
                        )
                    else: 
                        raise GraphQLError("Same service already being monitored")
                        
                    
                if input.apiType == 'REST':
                    restApiConfig = RestAPIConfig.objects.create(
                        method = input.apiType,
                        expected_status_code = input.expectedStatusCode
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
                headers = input.headers, 
                # authentication = authentication
                restApiConfig = restApiConfig,
                graphqlApiconfig = graphQlApiConfig,
                recipientDl = input.recipientDl,
                createdBy = input.createdBy,
                )

                # response = add.delay(2, 4, monitorApi.id)

                return ApiMonitorCreateMutation(monitoredApi = newMonitoredApi, success = True , message = "Api monitoring started")    
             except Exception as e:
                raise GraphQLError(f"{str(e)}")
                  
             