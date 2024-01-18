import graphene
from Business import schema 


class Query(schema.Query):
    pass


class Mutation(schema.Mutation):
    pass

schema = graphene.Schema(query = Query, mutation = Mutation )