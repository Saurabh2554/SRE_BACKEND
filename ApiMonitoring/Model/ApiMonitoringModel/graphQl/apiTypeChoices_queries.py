import graphene
from  ..apiMonitorModels import MonitoredAPI  # Import the Authentication model
  


class ApiTypeChoice(graphene.ObjectType):
    key = graphene.String()   # The actual value in the database
    value = graphene.String()


class Query(graphene.ObjectType):
    api_type_choices = graphene.List(ApiTypeChoice)

    def resolve_api_type_choices(self, info, **kwargs): 
        choices = MonitoredAPI.API_TYPE_CHOICES
        return [
            {'key': key, 'value': value} for key, value in choices
        ]