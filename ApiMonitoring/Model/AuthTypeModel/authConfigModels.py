from django.db import models

class Authentication(models.Model):
    AUTH_TYPE_CHOICES = [
        ('NONE', 'No Authentication'),
        ('API_KEY', 'API Key'),
        ('BASIC', 'Basic Authentication'),
        ('BEARER', 'Bearer Token (OAuth)'),
        ('CUSTOM', 'Custom Authentication'),
    ]

    auth_type = models.CharField(max_length=50, choices=AUTH_TYPE_CHOICES, default='NONE')  # Type of authentication

    # Fields for different types of authentication
    api_key = models.CharField(max_length=255, null=True, blank=True)  # API Key (for API Key Auth)
    basic_username = models.CharField(max_length=255, null=True, blank=True)  # Username (for Basic Auth)
    basic_password = models.CharField(max_length=255, null=True, blank=True)  # Password (for Basic Auth)
    bearer_token = models.TextField(null=True, blank=True)  # OAuth Bearer Token (for Bearer Token Auth)
    custom_auth_headers = models.JSONField(null=True, blank=True)  # Custom auth headers (for custom methods)

    def __str__(self):
        return f"{self.auth_type} Authentication"

