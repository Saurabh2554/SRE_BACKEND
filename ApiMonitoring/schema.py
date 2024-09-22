import graphene
from ApiMonitoring.Model.AuthTypeModel.graphQl import authChoices_queries
from ApiMonitoring.Model.ApiMonitoringModel.graphQl import queries
from ApiMonitoring.Model.ApiMonitoringModel.graphQl import mutations

class Query(authChoices_queries.Query, queries.Query):
   pass

class Mutation(graphene.ObjectType):   
   create_api_monitor = mutations.ApiMonitorCreateMutation.Field() 