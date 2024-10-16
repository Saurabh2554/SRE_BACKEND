import logging
from celery import shared_task
from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from Business.models import BusinessUnit, SubBusinessUnit
from ApiMonitoring.hitApi import hit_api
from graphql import GraphQLError
from celery import current_task
from celery.result import AsyncResult
from celery.worker.control import revoke
from celery.exceptions import Retry
from .hitApi import APIError
from ApiMonitoring.Model.ApiMonitoringModel.graphQl.helpers import SendEmailNotification, SendNotificationOnTeams

logger = logging.getLogger(__name__)
@shared_task
def revokeTask(taskId, serviceId):
    try:
        if taskId:
            task_result = AsyncResult(taskId)
            if task_result.state != 'REVOKED' :
                revoke(taskId, terminate=True)
                service = MonitoredAPI.objects.get(pk = serviceId)
                service.isApiActive = False
                service.save()

                return "Service Revoked"
            else:
                raise GraphQLError("Service is already revoked")
        else:
            raise GraphQLError("Invalid request!")

    except Exception as ex:
        raise GraphQLError(f"{ex}")
        
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def monitorApiTask(self, serviceId):
    try:
        service = MonitoredAPI.objects.get(pk =serviceId)    
        result = hit_api(service.apiUrl, service.apiType, service.headers)
        if result['success']:
            service.isApiActive = True
            service.taskId = current_task.request.id # Store the celery task Id
            service.save()
        #saving mertices--- 
            apiMetrices = APIMetrics.objects.create(
                api = service,
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

    except (APIError, Retry) as e:
        if self.request.retries == self.max_retries: # after 3 max retries
            revokeTask.delay(self.request.id , id) 
            # SendEmailNotification(id)
            # SendNotificationOnTeams(id)

        else:    
          self.retry()
    except Exception as ex:
        print(f"inside the main tast hitting api : {ex}")
        raise GraphQLError(
            f"{ex}"
        )  

@shared_task
def periodicMonitoring(serviceId):
    try:
        service = MonitoredAPI.objects.get(pk =serviceId)
        print(service.isApiActive, "service is active")  # or any other filter
        if service.isApiActive:  
          monitorApiTask.delay(service.id)

    except MonitoredAPI.DoesNotExist as e:
        
        raise Exception("Wrong service trigerred")    
    except Exception as e:
        print(f"inside the periodic task {e}")
        raise Exception("error scheduling tasks")    
    
#