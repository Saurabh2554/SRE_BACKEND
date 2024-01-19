import graphene
from .types import BusinessUnitType , SubBusinessUnitType 
from .models import BusinessUnit , SubBusinessUnit
from graphql import GraphQLError

# Create a business unit
class BusinessUnitCreateMutation(graphene.Mutation):
            class Arguments:
                businessUnitName = graphene.String(required = True)
                businessUnitDescription = graphene.String(required = True)
                businessUnitDl = graphene.String(required = True)
                createdBy = graphene.String(required = True)

           
            businessUnit = graphene.Field(BusinessUnitType)
            success = graphene.Boolean()
            message = graphene.String()

            def mutate(self, info, businessUnitName, businessUnitDescription,businessUnitDl,createdBy):
             try:

                businessUnit = BusinessUnit.objects.filter(businessUnitName__iexact=f'{businessUnitName}')
                
                if businessUnit.exists():
                    raise GraphQLError("Business with the same name already exist")
                     
                else:
                    businessUnit = BusinessUnit.objects.create (
                    businessUnitName=businessUnitName, 
                    businessUnitDescription=businessUnitDescription,
                    businessUnitDl = businessUnitDl,
                    createdBy = createdBy
                    )
                    return BusinessUnitCreateMutation(businessUnit=businessUnit,success = True , message = "Business unit created")    
             except Exception as e:
                raise GraphQLError(f"{str(e)}")
                  
             
#Update a Business Unit 
class BusinessUnitUpdateMutation(graphene.Mutation):
        id = graphene.UUID(required=True)
        businessUnitDescription = graphene.String(required = True)
        businessUnitDl = graphene.String(required = True)  

        businessUnit = graphene.Field(BusinessUnitType)
        success = graphene.Boolean()
        message = graphene.String()
        def mutate(seld , info,id,businessUnitDescription,businessUnitDl):
            try:
                if id is not None:
                    businessUnit = BusinessUnit.objects.get(pk=id)

                    if businessUnit is not None:
                        businessUnit.businessUnitDescription = businessUnitDescription
                        businessUnit.businessUnitDl = businessUnitDl

                        return BusinessUnitUpdateMutation(businessUnit)
                    else:
                        raise GraphQLError("Business Unit with the given id does not exist")
                    
                else:
                    raise GraphQLError("Id field is required")
            except Exception as e:
                 raise GraphQLError(f"{str(e)}")

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
            subBusinessUnit = SubBusinessUnit.objects.filter(subBusinessUnitName__iexact=f'{subBusinessUnitName}')
                
            if subBusinessUnit.exists():
                raise GraphQLError("Sub Business unit with the same name already exist")
            else:
             subBusinessUnit = SubBusinessUnit.objects.create (
                subBusinessUnitName=subBusinessUnitName, 
                subBusinessUnitDescription=subBusinessUnitDescription,
                subBusinessUnitDl = subBusinessUnitDl,
                createdBy = createdBy,
                businessUnitId = businessUnitId
                )
             return SubBusinessUnitCreateMutation(subBusinessUnit=subBusinessUnit)
         except Exception as e:
              raise GraphQLError(f"{str(e)}")

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
                       raise GraphQLError("Sub Business unit with the given id does not exist")
                  
             else:
                raise GraphQLError("Id field is required")
        except Exception as e:
            raise GraphQLError(f"{str(e)}")     