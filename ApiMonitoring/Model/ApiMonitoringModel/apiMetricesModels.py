from django.db import models
from ApiMonitoring.Model.ApiConfigModel.restApiConfigModels import RestAPIMetrics
from ApiMonitoring.Model.ApiConfigModel.graphQlApiConfigModels import GraphQLAPIMetrics
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI

class APIMetrics(models.Model):
    api = models.ForeignKey(MonitoredAPI, on_delete=models.CASCADE, related_name='metrics')  # Link to the API being monitored
    timestamp = models.DateTimeField(auto_now_add=True)  # Time when the metric was recorded

    # Common fields for both REST and GraphQL
    responseTime = models.FloatField(null=True, blank=True)  # Time taken to get a response
    success = models.BooleanField(default=False)  # Whether the request was successful
    errorMessage = models.TextField(null=True, blank=True)  # Error message if any
    
    # REST API-specific metrics
    rest_metrices =models.ForeignKey(RestAPIMetrics, on_delete=models.CASCADE, null=True, blank=True)  # Foreign key to Authentication
    
    
    # GraphQL-specific metrics
    graphql_metrices = models.ForeignKey(GraphQLAPIMetrics,on_delete=models.CASCADE,null=True, blank=True)
    
    def __str__(self):
        return f"Metrics for {self.api.name} at {self.timestamp}"
