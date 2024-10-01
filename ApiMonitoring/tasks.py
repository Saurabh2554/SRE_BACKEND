import logging
from celery import shared_task
from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
# from ApiMonitoring.Model.ApiConfigModel.restApiConfigModels import RestAPIMetrics
# from ApiMonitoring.Model.ApiConfigModel.graphQlApiConfigModels import GraphQLAPIMetrics
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from ApiMonitoring.hitApi import hit_api
from graphql import GraphQLError
import datetime

logger = logging.getLogger(__name__)



@shared_task
def monitorApi(apiUrl, apiType, headers, id):
    try:    
        result = hit_api(apiUrl, apiType, headers)
        monitoredApi = MonitoredAPI.objects.get(pk = id)

        # To check the validation for  isAPIActive
        # current_date = datetime.now(monitoredApi.createdAt.tzinfo)
        # api_duration = current_date - monitoredApi.createdAt

        # if api_duration.days > monitoredApi.apiMonitorDuration:
        #     monitoredApi.isApiActive = False
        #     monitoredApi.save()
        #     return f"API monitoring stopped for {monitoredApi.apiName} after exceeding {monitoredApi.apiMonitorDuration} days."

        # if not monitoredApi.isApiActive:
        #     return f"Monitoring skipped for {monitoredApi.apiName} as it is inactive."
        
        if monitoredApi is not None:
        #saving mertices--- 
            apiMetrices = APIMetrics.objects.create(
                api = monitoredApi,
                responseTime = result['response_time'],
                success = result['success'],
                statusCode = result['status'],
                errorMessage = result['error_message'],
                requestStartTime = result['start_time'],
                firstByteTime = result['end_time'],
                responseSize = result['response_size']
            )
            return "Monitored"
        else:
            pass

    except Exception as ex:
        raise GraphQLError(
            f"{ex}"
        )

        
        

    

    

@shared_task
def mul(x, y):
    return x * y

@shared_task
def xsum(numbers):
    return sum(numbers)