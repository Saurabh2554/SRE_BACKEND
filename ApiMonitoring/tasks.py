import logging
from celery import shared_task
from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from Business.models import BusinessUnit, SubBusinessUnit
from ApiMonitoring.hitApi import hit_api
from graphql import GraphQLError
from celery import current_task
from celery.result import AsyncResult
from celery.app.control import Control
from celery.exceptions import Retry
from ApiMonitoring.Model.ApiMonitoringModel.graphQl.helpers import get_service, PrepareContext, send_email, SendNotificationOnTeams, UpdateTask
from mySite.celery import app

logger = logging.getLogger(__name__)

@shared_task
def SendNotification(serviceId):
    try:
        service = get_service(serviceId)
    
        if not service:
            return

        apiMetrices = APIMetrics.objects.filter(api=service)
        context = PrepareContext(apiMetrices, service.apiName, service.apiUrl)

        send_email(service, context)
        SendNotificationOnTeams(context)

    except Exception as e:
        raise "Error sending notification!"    


@shared_task
def revokeTask(taskId, serviceId):
    try:
        if taskId:
            task_result = AsyncResult(taskId)
            if task_result.state != 'REVOKED' :

                control = Control(app = app)
                control.revoke(task_id = taskId, terminate=True)
                
                service = get_service(serviceId)
                service.isApiActive = False

                if service.taskId:
                  task_id = service.taskId.id
                  UpdateTask(task_id, False)
                
                service.save()
                
                SendNotification.delay(serviceId)

                return "Service Revoked"   
            else:
                return "Service is already revoked"
        else:
            return "Invalid request!"

    except Exception as ex:
        raise GraphQLError(f"{ex}")
        
@shared_task(bind=True, max_retries=3)
def monitorApiTask(self, serviceId):
    try: 
        payload = None
        service = get_service(serviceId) 
        
        if service.graphqlApiconfig:
            payload = service.graphqlApiconfig.graphql_query

        result = hit_api(service.apiUrl, service.apiType, service.headers, payload)

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
    
        if result['success']:
            return "Monitored"
        else:
            raise Retry("API call was not successful, retrying...") 

    except (Retry) as ex:
      try:
        if self.request.retries >= self.max_retries: # after 3 max retries
            revokeTask.delay(self.request.id , service.id) 

        else: 
          retry_delay =   50 * (2 ** self.request.retries)
          raise self.retry(exc =ex, countdown = 50) 

      except Exception as notification_error:
        print(f"inside nested exception................... {notification_error}")  

    except ValueError as ex:
       print(ex)    

    except Exception as ex:
        print(f"Error executing tasks : {ex}")
       

@shared_task
def periodicMonitoring(serviceId):
    try:
        service = get_service(serviceId)

        # if service.isApiActive:  
        monitorApiTask.delay(service.id)
 
    except MonitoredAPI.DoesNotExist as e:    
        print( "Wrong service trigerred"  )

    except Exception as e:
        print(f"error scheduling tasks: {e}")   
    
