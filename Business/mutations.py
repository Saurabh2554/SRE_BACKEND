import graphene
from .types import BusinessUnitType , SubBusinessUnitType 
from .models import BusinessUnit , SubBusinessUnit
from graphql import GraphQLError

class ValidationError(Exception):
    pass

def validatelength(Name, Description):
    if Name and len(Name)>50:
        raise ValidationError("Name should be less than 50 char.")
    if Description and len(Description)>100:
        raise ValidationError("Description should be less than 50 char.")

# Create a business unit
class BusinessUnitCreateMutation(graphene.Mutation):
    class Arguments:
        businessUnitName = graphene.String(required = True)
        businessUnitDescription = graphene.String(required = True)
        businessUnitDl = graphene.String(required = True)

    businessUnit = graphene.Field(BusinessUnitType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, businessUnitName, businessUnitDescription,businessUnitDl):
     try:

        businessUnit = BusinessUnit.objects.filter(businessUnitName__iexact=f'{businessUnitName}')

        if businessUnit.exists():
            raise ValidationError("Business with the same name already exist")

        validatelength(businessUnitName,businessUnitDescription)

        businessUnit = BusinessUnit.objects.create (
        businessUnitName=businessUnitName,
        businessUnitDescription=businessUnitDescription,
        businessUnitDl = businessUnitDl,
        )
        return BusinessUnitCreateMutation(businessUnit,success = True , message = "Business unit created")

     except ValidationError as ve:
         raise GraphQLError(str(ve))
     except Exception as e:
        raise GraphQLError(f"{str(e)}")
                  
             
#Update a Business Unit 
class BusinessUnitUpdateMutation(graphene.Mutation):
        id = graphene.UUID(required=True)
        businessUnitDescription = graphene.String()
        businessUnitDl = graphene.String()

        businessUnit = graphene.Field(BusinessUnitType)
        success = graphene.Boolean()
        message = graphene.String()
        def mutate(self, info, id, businessUnitDescription=None, businessUnitDl=None):
            try:
                if id is not None:
                    businessUnit = BusinessUnit.objects.get(pk=id)

                    if businessUnit is not None:

                        if businessUnitDescription:
                          validatelength(None, businessUnitDescription)
                          businessUnit.businessUnitDescription = businessUnitDescription
                        if businessUnitDl:
                          businessUnit.businessUnitDl = businessUnitDl

                        businessUnit.save()
                        return BusinessUnitUpdateMutation(businessUnit,success = True , message = "Business unit updated")
                    else:
                        raise ValidationError("Business Unit does not exist!")
                    
                else:
                    raise ValidationError("Id field is required")

            except ValidationError as ve:
              raise GraphQLError(str(ve))
            except Exception as e:
              raise GraphQLError(f"{str(e)}")

#Create Sub business Unit
class SubBusinessUnitCreateMutation(graphene.Mutation):
    class Arguments:
        subBusinessUnitName = graphene.String(required = True)
        subBusinessUnitDescription = graphene.String(required = True)
        subBusinessUnitDl = graphene.String(required = True)
        businessUnit = graphene.UUID(required = True)

    subBusinessUnit = graphene.Field(SubBusinessUnitType)
    success = graphene.Boolean()
    message = graphene.String()
    def mutate(self, info, subBusinessUnitName, subBusinessUnitDescription,subBusinessUnitDl, businessUnit):
         try:
            subBusinessUnit = SubBusinessUnit.objects.filter(subBusinessUnitName__iexact=f'{subBusinessUnitName}')
            businessUnitObj = BusinessUnit.objects.get(pk=businessUnit)   

            if subBusinessUnit.exists():
                raise ValidationError("Sub Business unit already exist!")
            
            if businessUnitObj is None:
                raise ValidationError("Incorrect Business unit given")

            validatelength(subBusinessUnitName, subBusinessUnitDescription)

            subBusinessUnit = SubBusinessUnit.objects.create (
                subBusinessUnitName=subBusinessUnitName,
                subBusinessUnitDescription=subBusinessUnitDescription,
                subBusinessUnitDl = subBusinessUnitDl,
                businessUnit = businessUnitObj
            )

            return SubBusinessUnitCreateMutation(subBusinessUnit=subBusinessUnit,success = True , message = "Sub Business unit created")

         except ValidationError as ve:
             raise GraphQLError(str(ve))
         except Exception as e:
             raise GraphQLError(f"{str(e)}")

#Update a Business Unit 
class SubBusinessUnitUpdateMutation(graphene.Mutation):
     id = graphene.UUID(required=True)
     subBusinessUnitDescription = graphene.String()
     subBusinessUnitDl = graphene.String()

     subBusinessUnit = graphene.Field(SubBusinessUnitType)
     success = graphene.Boolean()
     message = graphene.String()
     def mutate(self, info, id, subBusinessUnitDescription = None, subBusinessUnitDl = None):
        try:
             if id is not None:
                  subBusinessUnit = SubBusinessUnit.objects.get(pk=id)

                  if subBusinessUnit is not None:
                      if subBusinessUnitDescription:
                         validatelength(None, subBusinessUnitDescription)
                         subBusinessUnit.subBusinessUnitDescription = subBusinessUnitDescription
                      if subBusinessUnitDl:
                         subBusinessUnit.subBusinessUnitDl = subBusinessUnitDl

                      subBusinessUnit.save()
                      return SubBusinessUnitUpdateMutation(subBusinessUnit , success = True , mesage = "Sub business unit updated")
                  else:
                       raise ValidationError("Sub Business unit does not exist")
                  
             else:
                raise ValidationError("Id field is required")

        except ValidationError as ve:
            raise GraphQLError(str(ve))
        except Exception as e:
            raise GraphQLError(f"{str(e)}")     