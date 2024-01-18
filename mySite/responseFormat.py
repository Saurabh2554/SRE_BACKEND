import graphene

class ResponseFormat():
    status = graphene.Int()
    error = graphene.String()
    success = graphene.Boolean()
    