from django.db import models

class AssertionAndLimit(models.Model):
    expectedResponseTime = models.IntegerField(default=10, null=True, blank=True)
    degradedResponseTime = models.IntegerField(default=10, null=True, blank=True)
    failedResponseTime = models.IntegerField(default=10, null=True, blank=True)

    def __str__(self):
        return f"{self.expectedResponseTime}"
