import uuid
from django.db import models
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI

class AssertionAndLimit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api = models.ForeignKey(MonitoredAPI, on_delete=models.CASCADE, related_name='assertionAndLimit')
    degradedResponseTime = models.IntegerField(default=10, null=True, blank=True)
    failedResponseTime = models.IntegerField(default=10, null=True, blank=True)

    def __str__(self):
        return f"{self.degradedResponseTime}"
