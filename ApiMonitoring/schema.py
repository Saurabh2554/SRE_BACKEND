import graphene
from graphene_django import DjangoObjectType
from .models import BusinessUnit , SubBusinessUnit


class BusinessUnitType(DjangoObjectType):
    class Meta:
        model = BusinessUnit
        fields = "__all__"

class SubBusinessUnitType(DjangoObjectType):
    class Meta:
        model = SubBusinessUnit
        fields = "__all__"
        
                