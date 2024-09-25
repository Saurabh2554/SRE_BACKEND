from django.contrib import admin
from ApiMonitoring.Model.ApiConfigModel.graphQlApiConfigModels import GraphQLAPIConfig 
from ApiMonitoring.Model.ApiConfigModel.restApiConfigModels import RestAPIConfig 
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from ApiMonitoring.Model.AuthTypeModel.authConfigModels import Authentication
from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics


admin.site.register(Authentication)
# admin.site.register(GraphQLAPIMetrics)
admin.site.register(RestAPIConfig)
# admin.site.register(RestAPIMetrics)
admin.site.register(GraphQLAPIConfig)
admin.site.register(MonitoredAPI)
admin.site.register(APIMetrics)