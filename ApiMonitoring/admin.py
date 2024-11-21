from django.contrib import admin
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from ApiMonitoring.Model.AuthTypeModel.authConfigModels import Authentication
from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics


admin.site.register(Authentication)
admin.site.register(MonitoredAPI)
admin.site.register(APIMetrics)