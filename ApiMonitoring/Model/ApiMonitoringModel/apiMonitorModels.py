import uuid
from django.db import models
# from ApiMonitoring.Model.AuthTypeModel.authConfigModels import Authentication
from Business.models import BusinessUnit , SubBusinessUnit
from django.utils import timezone
from django_celery_beat.models import PeriodicTask
import os
from dotenv import load_dotenv

load_dotenv()


class MonitoredAPI(models.Model):
    METHOD_TYPE_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
    ]
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    businessUnit = models.ForeignKey(BusinessUnit ,on_delete = models.CASCADE)
    subBusinessUnit = models.ForeignKey(SubBusinessUnit ,on_delete = models.CASCADE)

    apiName = models.CharField(max_length=255, null=True, blank=True)  # API name
    apiUrl = models.URLField()  # Common URL field for both REST and GraphQL
    headers = models.JSONField(null=True, blank=True)  # Optional custom headers
    methodType = models.CharField(max_length=10, choices=METHOD_TYPE_CHOICES, default='GET')
    requestBody = models.TextField(null = True, blank = True) #

    # Tracking the monitoring status
    isApiActive = models.BooleanField(default=False)  # Status if API is being monitored or not

    degradedResponseTime = models.IntegerField(null=True, blank=True, help_text="Threshold in milliseconds")
    failedResponseTime = models.IntegerField(null=True, blank=True, help_text="Threshold in milliseconds")


    # Timestamps
    createdAt = models.DateTimeField(default=timezone.now)
    
    # task_related
    taskId = models.ForeignKey(PeriodicTask, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.apiName}"


