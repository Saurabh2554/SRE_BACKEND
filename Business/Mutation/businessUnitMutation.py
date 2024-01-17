import graphene
from ..schema import BusinessUnitType 
from ..models import BusinessUnit 

# Create a business unit
class BusinessUnitCreateMutation(graphene.Mutation):
            class Arguments:
                businessUnitName = graphene.String(max_length = 50 , required = True)
                businessUnitDescription = graphene.String(max_length = 100,required = True)
                businessUnitDl = graphene.String(required = True)
                createdBy = graphene.EmailField(required = True)

            businessUnit = graphene.Field(BusinessUnitType)

            def mutate(self, info, businessUnitName, businessUnitDescription,businessUnitDl,createdBy):

                businessUnit = BusinessUnit.objects.create (
                    businessUnitName=businessUnitName, 
                    businessUnitDescription=businessUnitDescription,
                    businessUnitDl = businessUnitDl,
                    createdBy = createdBy
                    )
                return BusinessUnitCreateMutation(businessUnit=businessUnit)    
    
#Update a Business Unit 
class BusinessUnitUpdateMutation(graphene.Mutation):
        id = graphene.UUID(required=True)
        businessUnitDescription = graphene.String(max_length = 100,required = True)
        businessUnitDl = graphene.String(required = True)  

        businessUnit = graphene.Field(BusinessUnitType)

        def mutate(seld , info,id,businessUnitDescription,businessUnitDl):
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



             