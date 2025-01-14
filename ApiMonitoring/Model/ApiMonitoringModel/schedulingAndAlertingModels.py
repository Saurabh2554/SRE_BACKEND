from django.db import models
import os
from dotenv import load_dotenv

load_dotenv()

class SchedulingAndAlerting(models.Model):
    apiCallInterval = models.IntegerField(default=5, null=True, blank=True)
    maxRetries = models.IntegerField(default=3, null=True, blank=True)
    retryAfter = models.IntegerField(default=60, null=True, blank=True)
    recipientDl = models.JSONField(null=False, blank=False)
    createdBy = models.EmailField(null=True, blank=True)
    teamsChannelWebhookURL = models.TextField(default=os.getenv('TEAMS_CHANNEL_WEBHOOK_URL'))

    def __str__(self):
        return f"{self.apiCallInterval}"
