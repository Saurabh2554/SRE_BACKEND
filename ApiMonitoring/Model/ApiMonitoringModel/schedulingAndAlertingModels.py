import os
import uuid
from django.db import models
from dotenv import load_dotenv
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI

load_dotenv()

class SchedulingAndAlerting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api = models.ForeignKey(MonitoredAPI, on_delete=models.CASCADE, related_name='schedulingAndAlerting')
    apiCallInterval = models.IntegerField(default=5, null=True, blank=True)
    maxRetries = models.IntegerField(default=3, null=True, blank=True)
    retryAfter = models.IntegerField(default=60, null=True, blank=True)
    recipientDl = models.JSONField(null=False, blank=False)
    createdBy = models.EmailField(null=True, blank=True)
    teamsChannelWebhookURL = models.TextField(default=os.getenv('TEAMS_CHANNEL_WEBHOOK_URL'),null=True, blank=True)

    def __str__(self):
        return f"{self.apiCallInterval}"
