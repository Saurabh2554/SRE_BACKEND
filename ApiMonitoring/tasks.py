
from celery import shared_task
import logging

from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
from ApiMonitoring.Model.ApiConfigModel.restApiConfigModels import RestAPIMetrics
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from ApiMonitoring.hitApi import hitRestApi
# Get an instance of a logger
logger = logging.getLogger(__name__)



@shared_task
def monitorApi(apiType, apiUrl, headers, id):
    if apiType == 'REST':
        
        result = hitRestApi(apiUrl)

        #saving mertices---
        monitoredApi = MonitoredApi.objects.get(pk = id)
        restApiMetrices = RestAPIMetrics.objects.create(
            status_code = result['status_code']
        )
        apiMetrices = APIMetrics.objects.create(
                api = monitorApi,
                responseTime = result['response_time'],
                success = True,
                rest_metrices = restApiMetrices
        )
    elif apiType == 'GraphQL':
        
        

    

    

@shared_task
def mul(x, y):
    return x * y

@shared_task
def xsum(numbers):
    return sum(numbers)