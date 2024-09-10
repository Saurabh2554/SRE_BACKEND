import graphene
from Business import schema as business_schema 


class Query(business_schema.Query):
    pass


class Mutation(business_schema.Mutation):
    pass

schema = graphene.Schema(query = Query, mutation = Mutation )