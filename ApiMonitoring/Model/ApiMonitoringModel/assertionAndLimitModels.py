import uuid
from django.db import models
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI


class AssertionAndLimit(models.Model):
    SOURCE_CHOICES = [
        ('status_code', 'Status Code'),
        ('headers', 'Headers'),
        ('json_body', 'JSON Body')

    ]
    OPERATOR_CHOICES = [
        ('equals', 'Equals'),
        ('not_equals', 'Not Equals'),
        ('greater_than', 'Greater Than'),
        ('less_than', 'Less Than'),
        ('contains', 'Contains'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api = models.ForeignKey(MonitoredAPI, on_delete=models.CASCADE, related_name='assertionAndLimit')

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, null=True, blank=True)
    property = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, null=True, blank=True)
    expectedValue = models.CharField(max_length=255, null=True, blank=True)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['api', 'source', 'property', 'operator'],
    #             name='unique_assertion_per_api'
    #         )
    #     ]

    def __str__(self):
        property_info = f" - {self.property}" if self.property else ""
        thresholds = f" (Degraded: {self.degradedResponseTime} ms, Failed: {self.failedResponseTime} ms)"
        return f"{self.source}{property_info}: {self.operator} {self.expectedValue}{thresholds}"
