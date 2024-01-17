import graphene
from ..schema import  SubBusinessUnitType


class Query(graphene.ObjectType):
    all_sub_business_unit = graphene.List(SubBusinessUnitType)
    sub_business_unit = graphene.Field(SubBusinessUnitType , id = graphene.UUID(required = True))

#Get all sub-business unit objects
    def resolve_all_sub_business_unit(root , info):
        return SubBusinessUnitType.objects.all()
    
#Retreive single sub-business unit object based on id
    def sub_business_unit(root , info,**kwargs):
        id = kwargs.get('id')

        if id is not None:
            return SubBusinessUnitType.objects.get(pk = id)

        return None 
