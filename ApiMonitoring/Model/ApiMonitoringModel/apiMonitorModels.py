import uuid
from django.db import models
from ApiMonitoring.Model.ApiConfigModel.restApiConfigModels import RestAPIConfig
from ApiMonitoring.Model.ApiConfigModel.graphQlApiConfigModels import GraphQLAPIConfig
from ApiMonitoring.Model.AuthTypeModel.authConfigModels import Authentication
from Business.models import BusinessUnit , SubBusinessUnit
from django.utils import timezone

class MonitoredAPI(models.Model):
    API_TYPE_CHOICES = [
        ('REST', 'REST API'),
        ('GraphQL', 'GraphQL API'),
    ]
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    businessUnit = models.ForeignKey(BusinessUnit ,on_delete = models.CASCADE)
    subBusinessUnit = models.ForeignKey(SubBusinessUnit ,on_delete = models.CASCADE)
    apiName = models.CharField(max_length=255, null=True, blank=True)  # API name
    apiType = models.CharField(max_length=50, choices=API_TYPE_CHOICES)  # Type of API
    apiUrl = models.URLField()  # Common URL field for both REST and GraphQL
    
    
    # Monitoring settings
    apiCallInterval = models.IntegerField(default=5, null=True, blank=True)  # Monitoring interval in min
    expectedResponseTime = models.IntegerField(default=10, null=True, blank=True)  # Request timeout in ms
    headers = models.JSONField(null=True, blank=True)  # Optional custom headers

    # Link to authentication system
    # authentication = models.ForeignKey(Authentication, on_delete=models.SET_NULL, null=True, blank=True)  # Foreign key to Authentication
    
    # REST and GraphQL-specific configurations
    restApiConfig = models.ForeignKey(RestAPIConfig, on_delete=models.CASCADE, null=True, blank=True)
    graphqlApiconfig = models.ForeignKey(GraphQLAPIConfig, on_delete=models.CASCADE, null=True, blank=True)

    # Tracking the monitoring status
    isApiActive = models.BooleanField(default=False)  # Status if API is being monitored or not

    # Timestamps
    createdAt = models.DateTimeField(default=timezone.now)
    
    # owner
    recipientDl = models.EmailField(null = False , blank = False)
    createdBy = models.EmailField(null = False , blank = True)


    def __str__(self):
        return f"{self.apiName} ({self.apiType})"


