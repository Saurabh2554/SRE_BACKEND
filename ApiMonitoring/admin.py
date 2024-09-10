from django.contrib import admin
from .Model import GraphQLAPIConfig, GraphQLAPIMetrics, RestAPIConfig, RestAPIMetrics,Authentication

admin.site.register(Authentication)
admin.site.register(GraphQLAPIMetrics)
admin.site.register(RestAPIConfig)
admin.site.register(RestAPIMetrics)
admin.site.register(GraphQLAPIConfig)