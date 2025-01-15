import uuid
from django.db import models
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from django.utils import timezone

class APIMetrics(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api = models.ForeignKey(MonitoredAPI, on_delete=models.CASCADE, related_name='metrics')  # Link to the API being monitored
    timestamp = models.DateTimeField(default = timezone.now)  # Time when the metric was recorded

   # for calculating latency
    requestStartTime = models.DateTimeField(default = timezone.now)
    firstByteTime = models.DateTimeField(default = timezone.now)

    responseTime = models.FloatField(null=True, blank=True)  # Time taken to get a response
    success = models.BooleanField(default=False)  # Whether the request was successful
    errorMessage = models.TextField(null=True, blank=True)  # Error message if any
    statusCode = models.IntegerField(null=True, blank=True)
    responseSize = models.IntegerField(default = 233, null=True, blank=True)
    failed = models.BooleanField(default=False, null=True, blank=True)
    degraded = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"Metrics for {self.responseTime} : {self.timestamp}"
