import uuid
from django.db import models
# from ApiMonitoring.Model.AuthTypeModel.authConfigModels import Authentication
from Business.models import BusinessUnit , SubBusinessUnit
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule
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
    
    
    # Monitoring settings
    apiCallInterval = models.IntegerField(default=5, null=True, blank=True)  # Monitoring interval in min
    expectedResponseTime = models.IntegerField(default=10, null=True, blank=True)  # Request timeout in ms
    headers = models.JSONField(null=True, blank=True)  # Optional custom headers

    # Link to authentication system
    # authentication = models.ForeignKey(Authentication, on_delete=models.SET_NULL, null=True, blank=True)  # Foreign key to Authentication
    
    methodType = models.CharField(max_length=10, choices=METHOD_TYPE_CHOICES)
    requestBody = models.TextField(null = True, blank = True) #

    # Tracking the monitoring status
    isApiActive = models.BooleanField(default=False)  # Status if API is being monitored or not

    # Timestamps
    createdAt = models.DateTimeField(default=timezone.now)
    
    # owner
    maxRetries = models.IntegerField(default = 3, null=True, blank=True)
    retryAfter = models.IntegerField(default = 60, null = True, blank = True)
    recipientDl = models.JSONField(null = False , blank = False)
    createdBy = models.EmailField(null = True , blank = True)
    teamsChannelWebhookURL = models.TextField(default = os.getenv('TEAMS_CHANNEL_WEBHOOK_URL'))

    taskId = models.ForeignKey(PeriodicTask, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.apiName}"


