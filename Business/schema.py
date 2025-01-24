import graphene
from .models import BusinessUnit , SubBusinessUnit
from .types import BusinessUnitType , SubBusinessUnitType
from .mutations import BusinessUnitCreateMutation,BusinessUnitUpdateMutation, SubBusinessUnitCreateMutation,SubBusinessUnitUpdateMutation
from graphql import GraphQLError 

     
                
class Query(graphene.ObjectType):
    sub_business_unit = graphene.Field(SubBusinessUnitType , id = graphene.UUID())
    business_unit = graphene.List(BusinessUnitType , id = graphene.UUID())
    sub_business_unit_per_business_unit = graphene.List(SubBusinessUnitType , id = graphene.UUID(required = True))

#Get all business unit objects
    def resolve_business_unit(root , info, **kwargs):
        try:
           BusinessUnitId = kwargs.get('id')

           if BusinessUnitId:
               return BusinessUnit.objects.filter(id = BusinessUnitId)
           else:
             return BusinessUnit.objects.all()
        except Exception as e:
            raise GraphQLError(f"{str(e)}")

#Get all sub-business unit objects
    def resolve_sub_business_unit(root , info):
        try:

            return SubBusinessUnit.objects.all()
        except Exception as e:
            raise GraphQLError(f"{str(e)}")


# Retrieve all sub business unit which comes under a particular business unit---
    def resolve_sub_business_unit_per_business_unit(root , info , **kwargs):
        try:
            BusinessUnitId = kwargs.get('id')
            if BusinessUnitId is not None:
              return SubBusinessUnit.objects.filter(businessUnit=f'{BusinessUnitId}')
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
