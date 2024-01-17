import graphene
from ..schema import SubBusinessUnitType 
from ..models import SubBusinessUnit 


#Create Sub business Unit
class SubBusinessUnitCreateMutation(graphene.Mutation):
    class Arguments:
        subBusinessUnitName = graphene.String(max_length = 50 , required = True)
        subBusinessUnitDescription = graphene.String(max_length = 100,required = True)
        subBusinessUnitDl = graphene.String(required = True)
        createdBy = graphene.EmailField(required = True)
        businessUnitId = graphene.UUID(required = True)

        subBusinessUnit = graphene.Field(SubBusinessUnitType)

        def mutate(self, info, subBusinessUnitName, subBusinessUnitDescription,subBusinessUnitDl,createdBy, businessUnitId):
             subBusinessUnit = SubBusinessUnit.objects.create (
                subBusinessUnitName=subBusinessUnitName, 
                subBusinessUnitDescription=subBusinessUnitDescription,
                subBusinessUnitDl = subBusinessUnitDl,
                createdBy = createdBy,
                businessUnitId = businessUnitId
                )
             return SubBusinessUnitCreateMutation(subBusinessUnit=subBusinessUnit)
        

#Update a Business Unit 
class SubBusinessUnitUpdateMutation(graphene.Mutation):
        id = graphene.UUID(required=True)
        subBusinessUnitDescription = graphene.String(max_length = 100,required = True)
        subBusinessUnitDl = graphene.String(required = True)  

        subBusinessUnit = graphene.Field(SubBusinessUnitType)

        def mutate(seld , info,id,subBusinessUnitDescription,subBusinessUnitDl):
             if id is not None:
                  subBusinessUnit = SubBusinessUnit.objects.get(pk=id)

                  if subBusinessUnit is not None:
                       subBusinessUnit.subBusinessUnitDescription = subBusinessUnitDescription
                       subBusinessUnit.subBusinessUnitDl = subBusinessUnitDl

                       return SubBusinessUnitUpdateMutation(subBusinessUnit)
                  else:
                       return {}
                  
             else:
                  return {}



                     