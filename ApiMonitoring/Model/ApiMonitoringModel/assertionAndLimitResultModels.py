import uuid
from django.db import models
from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
from ApiMonitoring.Model.ApiMonitoringModel.assertionAndLimitModels import AssertionAndLimit

class AssertionAndLimitResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assertion_and_limit = models.ForeignKey(AssertionAndLimit, on_delete=models.CASCADE, null=False)
    apimetrics = models.ForeignKey(APIMetrics, on_delete=models.CASCADE, null=False)
    actual_value = models.TextField(null=True)
    status = models.BooleanField(default=False)  # True for Passed, False for Failed
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"API: {self.assertion_and_limit.api.apiName} - {self.assertion_and_limit.source} - {'Passed' if self.status else 'Failed'}"