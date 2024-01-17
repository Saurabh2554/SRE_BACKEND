import graphene
import Business.Query.businessUnitQuery , Business.Query.businessUnitQuery
import Business.Mutation.businessUnitMutation , Business.Mutation.subBusinessUnitMutation

class ConbinedQuery(Business.Query.businessUnitQuery ,Business.Query.businessUnitQuery, graphene.ObjectType):
    pass


class ConbinedMutation(Business.Mutation.businessUnitMutation,Business.Mutation.subBusinessUnitMutation,graphene.ObjectType):
    pass

schema = graphene.Schema(query = ConbinedQuery , mutation = ConbinedMutation)