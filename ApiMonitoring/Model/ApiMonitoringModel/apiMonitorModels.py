import uuid
from django.db import models
from ..ApiConfigModel.restApiConfigModels import RestAPIConfig
from ..ApiConfigModel.graphQlApiConfigModels import GraphQLAPIConfig
from ..AuthTypeModel.authConfigModels import Authentication
from Business.models import BusinessUnit , SubBusinessUnit


class MonitoredAPI(models.Model):
    API_TYPE_CHOICES = [
        ('REST', 'REST API'),
        ('GraphQL', 'GraphQL API'),
    ]
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    businessUnit = models.ForeignKey(BusinessUnit ,on_delete = models.CASCADE)
    subBusinessUnit = models.ForeignKey(SubBusinessUnit ,on_delete = models.CASCADE)
    apiName = models.CharField(max_length=255)  # API name
    apiType = models.CharField(max_length=50, choices=API_TYPE_CHOICES)  # Type of API
    apiUrl = models.URLField()  # Common URL field for both REST and GraphQL
    
    
    # Monitoring settings
    apiCallInterval = models.IntegerField(default=5)  # Monitoring interval in min
    expectedResponseTime = models.IntegerField(default=10)  # Request timeout in ms
    headers = models.JSONField(null=True, blank=True)  # Optional custom headers

    # Link to authentication system
    authentication = models.ForeignKey(Authentication, on_delete=models.SET_NULL, null=True, blank=True)  # Foreign key to Authentication
    
    # REST and GraphQL-specific configurations
    restApiConfig = models.OneToOneField(RestAPIConfig, on_delete=models.CASCADE, null=True, blank=True)
    graphqlApiconfig = models.OneToOneField(GraphQLAPIConfig, on_delete=models.CASCADE, null=True, blank=True)

    # Timestamps
    createdAt = models.DateTimeField(default=timezone.now)
    
    # owner
    recipientDl = models.EmailField(null = False , blank = False)
    createdBy = models.EmailField(null = False , blank = True)

    def __str__(self):
        return f"{self.name} ({self.api_type})"


