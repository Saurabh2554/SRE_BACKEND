import uuid
from django.db import models
from Business.models import BusinessUnit , SubBusinessUnit 
from django.utils import timezone

class ApiRequestDetails(models.Model):
     id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
     BusinessUnitId = models.ForeignKey(BusinessUnit ,on_delete = models.CASCADE)
     subBusinessUnitId = models.ForeignKey(SubBusinessUnit ,on_delete = models.CASCADE)
     apiName = models.CharField(max_length = 100 , null = False , blank = False)
     apiUrl = models.CharField(max_length= 100 , null = False , blank = False)
     expectedResponseTime = models.IntegerField(null = False , blank = False)
     requestPayload = models.JSONField(blank = False , null = False)
     apiCallInterval = models.IntegerField(blank = False , null  = False)
     createdAt = models.DateTimeField(default=timezone.now)
     createdBy = models.EmailField(null = False , blank = True)
     recipientDl = models.EmailField(null = False , blank = False)


     def __str__(self)->str:
          return self.apiName