import logging
from celery import shared_task
from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from ApiMonitoring.hitApi import hit_api
from graphql import GraphQLError
from celery import current_task
from celery.result import AsyncResult
from celery.worker.control import revoke
import datetime

logger = logging.getLogger(__name__)

def revokeTask(taskId):
    try:
        if taskId:
            task_result = AsyncResult(taskId)
            if task_result.state is not 'REVOKED' :
                revoke(taskId, terminate=True)
            else:
                raise GraphQLError("Service is already revoked")
        else:
            raise GraphQLError("Invalid request!")

    except Exception as ex:
        raise GraphQLError(f"{ex}")
        

@shared_task
def monitorApi(apiUrl, apiType, headers, id):
    try:    
        result = hit_api(apiUrl, apiType, headers)
        if result.success:
            monitoredApi = MonitoredAPI.objects.get(pk = id)
        
            if monitoredApi.exists():
                monitoredApi.isApiActive = True
                monitoredApi.taskId = current_task.request.id # Store the celery task Id
                monitoredApi.save()
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
        print("inside the exception")
        raise GraphQLError(
            f"{ex}"
        )

        
        

    

    

# @shared_task
# def mul(x, y):
#     return x * y

# @shared_task
# def xsum(numbers):
#     return sum(numbers)