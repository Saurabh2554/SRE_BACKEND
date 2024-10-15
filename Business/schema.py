import graphene
from .models import BusinessUnit , SubBusinessUnit
from .types import BusinessUnitType , SubBusinessUnitType
from .mutations import BusinessUnitCreateMutation,BusinessUnitUpdateMutation, SubBusinessUnitCreateMutation,SubBusinessUnitUpdateMutation
from graphql import GraphQLError 
from ApiMonitoring.tasks import SendEmailNotification

     
                
class Query(graphene.ObjectType):
    all_sub_business_unit = graphene.List(SubBusinessUnitType )
    sub_business_unit = graphene.Field(SubBusinessUnitType , id = graphene.UUID(required = True))
    all_business_unit = graphene.List(BusinessUnitType)
    business_unit = graphene.Field(BusinessUnitType , id = graphene.UUID(required = True))
    sub_business_unit_per_business_unit = graphene.List(SubBusinessUnitType , id = graphene.UUID(required = True))

#Get all business unit objects
    def resolve_all_business_unit(root , info):
        try:
         SendEmailNotification('5736b749-40ac-48de-8a2d-f5033ea1d4e1')
         return BusinessUnit.objects.all()
        except Exception as e:
            return None   
 
#Retreive single business unit object based on id
    def resolve_business_unit(root , info,**kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
             return BusinessUnit.objects.get(pk = id)
            else:
              raise GraphQLError("Id field is required") 
        except Exception as e:
            raise GraphQLError(f"{str(e)}")

#Get all sub-business unit objects
    def resolve_all_sub_business_unit(root , info):
        try:
            return SubBusinessUnit.objects.all()
        except Exception as e:
            raise GraphQLError(f"{str(e)}")
          
#Retreive single sub-business unit object based on id
    def resolve_sub_business_unit(root , info,**kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
              return SubBusinessUnit.objects.get(pk = id)
            else:
              raise GraphQLError("Id field is required") 
        except Exception as e:
            raise GraphQLError(f"{str(e)}")


# Retreive all sub business unit which comes under a particular business unit---
    def resolve_sub_business_unit_per_business_unit(root , info , **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
              return SubBusinessUnit.objects.filter(businessUnit=f'{id}')
            else:
              raise GraphQLError("Id field is required") 
        except Exception as e:
            raise GraphQLError(f"{str(e)}")
        

# Mutation class exposing mutations
class Mutation(graphene.ObjectType):
    create_business_unit = BusinessUnitCreateMutation.Field() 
    update_business_unit= BusinessUnitUpdateMutation.Field()   
    create_subBusiness_unit = SubBusinessUnitCreateMutation.Field() 
    update_subBusiness_unit= SubBusinessUnitUpdateMutation.Field()     
