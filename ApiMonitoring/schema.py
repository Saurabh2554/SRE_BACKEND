import graphene
from .Model.AuthTypeModel.graphQl import authChoices_queries
from .Model.ApiMonitoringModel.graphQl import apiTypeChoices_queries
from .Model.ApiMonitoringModel.graphQl import mutations

class Query(authChoices_queries.Query, apiTypeChoices_queries.Query):
   pass

class Mutation(graphene.ObjectType):   
   create_api_monitor = mutations.ApiMonitorCreateMutation.Field() 