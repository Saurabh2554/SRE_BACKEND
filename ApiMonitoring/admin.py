from django.contrib import admin
from .Model.ApiConfigModel.graphQlApiConfigModels import GraphQLAPIConfig, GraphQLAPIMetrics 
from .Model.ApiConfigModel.restApiConfigModels import RestAPIConfig, RestAPIMetrics 
from .Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from .Model.AuthTypeModel.authConfigModels import Authentication

admin.site.register(Authentication)
admin.site.register(GraphQLAPIMetrics)
admin.site.register(RestAPIConfig)
admin.site.register(RestAPIMetrics)
admin.site.register(GraphQLAPIConfig)
admin.site.register(MonitoredAPI)
