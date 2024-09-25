import graphene
from  ApiMonitoring.Model.AuthTypeModel.authConfigModels import Authentication  # Import the Authentication model
  


class AuthTypeChoice(graphene.ObjectType):
    key = graphene.String()   # The actual value in the database
    value = graphene.String()


class Query(graphene.ObjectType):
    auth_type_choices = graphene.List(AuthTypeChoice)

    def resolve_auth_type_choices(self, info, **kwargs): 
        choices = Authentication.AUTH_TYPE_CHOICES
        return [
            {'key': key, 'value': value} for key, value in choices
        ]