from django.db import models


class RestAPIConfig(models.Model):
    method = models.CharField(max_length=10, default='GET')  # HTTP method for REST API
    expected_status_code = models.IntegerField(default=200)  # Expected HTTP status code
    
    def __str__(self):
        return f"REST Config (Method: {self.method}, Expected Status: {self.expected_status_code})"



class RestAPIMetrics(models.Model):
    status_code = models.IntegerField(null=True, blank=True)  # HTTP status code
    # response_payload = models.JSONField(null=True, blank=True)  # REST API response payload

    def __str__(self):
        return f"REST Metrics (Status Code: {self.status_code})"                