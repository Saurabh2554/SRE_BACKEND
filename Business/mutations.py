import graphene
from .types import BusinessUnitType , SubBusinessUnitType
from .models import BusinessUnit , SubBusinessUnit


# Create a business unit
class BusinessUnitCreateMutation(graphene.Mutation):
            class Arguments:
                businessUnitName = graphene.String(required = True)
                businessUnitDescription = graphene.String(required = True)
                businessUnitDl = graphene.String(required = True)
                createdBy = graphene.String(required = True)

            businessUnit = graphene.Field(BusinessUnitType)
           
            def mutate(self, info, businessUnitName, businessUnitDescription,businessUnitDl,createdBy):
             try:
                businessUnit = BusinessUnit.objects.create (
                    businessUnitName=businessUnitName, 
                    businessUnitDescription=businessUnitDescription,
                    businessUnitDl = businessUnitDl,
                    createdBy = createdBy
                    )
                return BusinessUnitCreateMutation(businessUnit=businessUnit)    
             except:
                  return None
             
#Update a Business Unit 
class BusinessUnitUpdateMutation(graphene.Mutation):
        id = graphene.UUID(required=True)
        businessUnitDescription = graphene.String(required = True)
        businessUnitDl = graphene.String(required = True)  

        businessUnit = graphene.Field(BusinessUnitType)

        def mutate(seld , info,id,businessUnitDescription,businessUnitDl):
            try:
                if id is not None:
                    businessUnit = BusinessUnit.objects.get(pk=id)

                    if businessUnit is not None:
                        businessUnit.businessUnitDescription = businessUnitDescription
                        businessUnit.businessUnitDl = businessUnitDl

                        return BusinessUnitUpdateMutation(businessUnit)
                    else:
                        return {}
                    
                else:
                    return {}
            except:
                 return None

#Create Sub business Unit
class SubBusinessUnitCreateMutation(graphene.Mutation):
    class Arguments:
        subBusinessUnitName = graphene.String(required = True)
        subBusinessUnitDescription = graphene.String(required = True)
        subBusinessUnitDl = graphene.String(required = True)
        createdBy = graphene.String(required = True)
        businessUnitId = graphene.UUID(required = True)

    subBusinessUnit = graphene.Field(SubBusinessUnitType)

    def mutate(self, info, subBusinessUnitName, subBusinessUnitDescription,subBusinessUnitDl,createdBy, businessUnitId):
         try:
             subBusinessUnit = SubBusinessUnit.objects.create (
                subBusinessUnitName=subBusinessUnitName, 
                subBusinessUnitDescription=subBusinessUnitDescription,
                subBusinessUnitDl = subBusinessUnitDl,
                createdBy = createdBy,
                businessUnitId = businessUnitId
                )
             return SubBusinessUnitCreateMutation(subBusinessUnit=subBusinessUnit)
         except:
              return None

#Update a Business Unit 
class SubBusinessUnitUpdateMutation(graphene.Mutation):
     id = graphene.UUID(required=True)
     subBusinessUnitDescription = graphene.String(required = True)
     subBusinessUnitDl = graphene.String(required = True)  

     subBusinessUnit = graphene.Field(SubBusinessUnitType)

     def mutate(seld , info,id,subBusinessUnitDescription,subBusinessUnitDl):
        try:
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
        except:
            return None     