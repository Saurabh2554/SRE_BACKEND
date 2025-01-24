from graphene_django import DjangoObjectType
from .models import BusinessUnit , SubBusinessUnit

class BusinessUnitType(DjangoObjectType):
    class Meta:
      model = BusinessUnit
      fields = ["id", "businessUnitName","businessUnitDescription"]

class SubBusinessUnitType(DjangoObjectType):
    class Meta:
      model = SubBusinessUnit
      fields = ["id", "subBusinessUnitName","subBusinessUnitDescription","businessUnit"]

     