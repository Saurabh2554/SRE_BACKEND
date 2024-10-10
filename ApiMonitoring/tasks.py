import logging
from celery import shared_task
from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from ApiMonitoring.hitApi import hit_api
from graphql import GraphQLError
from celery import current_task
from celery.result import AsyncResult
from celery.worker.control import revoke
from celery.exceptions import Retry
from .hitApi import APIError

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
        
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def monitorApiTask(apiUrl, apiType, headers, id):
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
            raise Retry("API call was not successful, retrying...")

    except (ApiError, Retry) as e:
        self.retry()
    except Exception as ex:
        raise GraphQLError(
            f"{ex}"
        )  

@shared_task
def periodicMonitoring():
    try:
        active_monitors = MonitoredAPI.objects.filter(isApiActive=True)  # or any other filter
        for monitor in active_monitors:
          monitorApiTask.apply_async((monitor.api_url, monitor.api_type, monitor.headers, monitor.id))
    except Exception as e:
        raise Exception("error scheduling tasks")    
    