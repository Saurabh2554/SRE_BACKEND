import graphene
from Business import schema as business_schema 
from ApiMonitoring import schema as apiMonitoring_schema


class Query(business_schema.Query,apiMonitoring_schema.Query):
    pass


class Mutation(business_schema.Mutation, apiMonitoring_schema.Mutation):
    pass

schema = graphene.Schema(query = Query, mutation = Mutation )