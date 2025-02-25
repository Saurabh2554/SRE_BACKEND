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
    ('is_empty', 'Is Empty'),
    ('is_not_empty', 'Is Not Empty'),
    ('greater_than', 'Greater Than'),
    ('less_than', 'Less Than'),
    ('contains', 'Contains'),
    ('not_contains', 'Not Contains'),
    ('is_null', 'Is Null'),
    ('is_not_null', 'Is Not Null'),
 ]
   

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api = models.ForeignKey(MonitoredAPI, on_delete=models.CASCADE, related_name='assertionAndLimit')

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, null=True, blank=True)
    property = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, null=True, blank=True)
    expectedValue = models.CharField(max_length=255, null=True, blank=True)
    regex  = models.TextField(null=True, blank=True)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['api', 'source', 'property', 'operator'],
    #             name='unique_assertion_per_api'
    #         )
    #     ]

    def __str__(self):
        property_info = f" - {self.property}" if self.property else ""
        return f"{self.source}{property_info}"
