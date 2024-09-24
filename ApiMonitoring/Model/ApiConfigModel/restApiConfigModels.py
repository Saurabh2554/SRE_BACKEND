from django.db import models


class RestAPIConfig(models.Model):
    method = models.CharField(max_length=10, default='GET')  # HTTP method for REST API
    expected_status_code = models.IntegerField()
    def __str__(self):
        return f"REST Config (Method: {self.method})"



# class RestAPIMetrics(models.Model):
#     status_code = models.IntegerField(null=True, blank=True)  # HTTP status code
    

#     def __str__(self):
#         return f"REST Metrics (Status Code: {self.status_code})"                