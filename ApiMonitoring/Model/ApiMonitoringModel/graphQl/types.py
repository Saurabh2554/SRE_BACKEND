from graphene_django import DjangoObjectType
from  ..apiMonitorModels import MonitoredAPI  # Import the Authentication model

class MoniterApiType(DjangoObjectType):
    class Meta:
      model = MonitoredAPI
      fields = "__all__"

# class SubBusinessUnitType(DjangoObjectType):
#     class Meta:
#       model = SubBusinessUnit
#       fields = "__all__"
