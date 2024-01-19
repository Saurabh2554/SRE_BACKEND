import uuid
from django.db import models


# Business Unit Model
class BusinessUnit(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    businessUnitName = models.CharField(max_length = 50 , blank=False,null = False)
    businessUnitDescription = models.CharField(max_length = 100,blank=False,null = False)
    businessUnitDl = models.EmailField(blank=False, null=False)
    createdBy = models.EmailField(blank=False, null=False)

    def __str__(self) ->str:
        return self.businessUnitName
    

# Sub Business Unit Model 
class SubBusinessUnit(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subBusinessUnitName = models.CharField(max_length = 50 , blank= False,null=False)
    subBusinessUnitDescription = models.CharField(max_length = 100,blank= False,null=False)
    subBusinessUnitDl = models.EmailField(blank=False, null=False)
    businessUnit = models.ForeignKey(BusinessUnit ,on_delete = models.CASCADE)
    createdBy = models.EmailField(blank=False, null=False)

    def __str__(self) ->str:
        return self.subBusinessUnitName    