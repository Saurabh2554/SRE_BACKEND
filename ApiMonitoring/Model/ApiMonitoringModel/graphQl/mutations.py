import graphene
from .types import MoniterApiType 
from  ..apiMonitorModels import MonitoredAPI 
from  ...ApiConfigModel.restApiConfigModels import RestAPIConfig
from  ...ApiConfigModel.graphQlApiConfigModels import GraphQLAPIConfig
from  Business.models import BusinessUnit , SubBusinessUnit
from graphql import GraphQLError


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
                monitoredApi = MonitoredAPI.objects.filter(
                    apiUrl__iexact=f'{input.apiUrl}'
                    )
                businessUnit = BusinessUnit.objects.get(pk = input.businessUnit)
                subBusinessUnit = SubBusinessUnit.objects.get(pk = input.subBusinessUnit)
                

                # print(businessUnit,subBusinessUnit,"gggggggggggggggggg")
                
                if monitoredApi.exists():
                    raise GraphQLError("Api with the same url already exists")

                if input.apiType == 'REST':
                    restApiConfig = RestAPIConfig.objects.create(
                        method = input.apiType,
                        expected_status_code = input.expectedStatusCode
                    )

                if input.apiType == 'GraphQL':
                    graphQlApiConfig = GraphQLAPIConfig.objects.create(
                    graphql_query = input.graphqlQuery
                        
                    )    

                
                monitoredApi = MonitoredAPI.objects.create(
                businessUnit=businessUnit, 
                subBusinessUnit = subBusinessUnit,
                apiName = input.apiName,
                apiType = input.apiType,
                apiUrl = input.apiUrl, 
                apiCallInterval = input.apiCallInterval, 
                expectedResponseTime = input.expectedResponseTime,  
                headers = input.headers, 
                # authentication = input.authentication
                restApiConfig = restApiConfig,
                graphqlApiconfig = graphQlApiConfig,
                recipientDl = input.recipientDl,
                createdBy = input.createdBy,
                )
                return ApiMonitorCreateMutation(monitoredApi = monitoredApi, success = True , message = "New api monitoring started")    
             except Exception as e:
                raise GraphQLError(f"{str(e)}")
                  
             