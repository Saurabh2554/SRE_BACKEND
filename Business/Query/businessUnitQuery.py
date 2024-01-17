import graphene
from ..schema import BusinessUnitType 


class Query(graphene.ObjectType):
    all_business_unit = graphene.List(BusinessUnitType)
    business_unit = graphene.Field(BusinessUnitType , id = graphene.UUID(required = True))
    
 
#Get all business unit objects
    def resolve_all_business_unit(root , info):
        return BusinessUnitType.objects.all()
    
    
#Retreive single business unit object based on id
    def business_unit(root , info,**kwargs):
        id = kwargs.get('id')

        if id is not None:
            return BusinessUnitType.objects.get(pk = id)

        return None 
