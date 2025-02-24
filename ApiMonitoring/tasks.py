<<<<<<< HEAD
import logging
from celery import shared_task
from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
from ApiMonitoring.Model.ApiMonitoringModel.assertionAndLimitModels import AssertionAndLimit
from ApiMonitoring.hitApi import hit_api
from graphql import GraphQLError
from celery.result import AsyncResult
from celery.app.control import Control
from celery.exceptions import Retry
from ApiMonitoring.Model.ApiMonitoringModel.graphQl.helpers import get_service, PrepareContext, send_email, SendNotificationOnTeams, UpdateTask
from mySite.celery import app
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

logger = logging.getLogger(__name__)

# def send_metrics_update(metrics_data):
#     try:
#         channel_layer = get_channel_layer()

#         room_group_name = f"metrics_data"

#         async_to_sync(channel_layer.group_send)(
#             room_group_name,
#             {
#                 "type": "send_metrics_update",
#                 "metrics": metrics_data,  
#             }
#         )
#     except:
#         pass

@shared_task
def SendNotification(serviceId, retryAttempts = None):
    try:
        service = get_service(serviceId)
        cc_email = []
        if not service:
            return

        apiMetrices = APIMetrics.objects.filter(api=service)
        context = PrepareContext(apiMetrices, service.apiName, service.apiUrl, serviceId)
        
        if retryAttempts ==2:
            cc_email = [service.subBusinessUnit.subBusinessUnitDl]  
        else:
            cc_email = [service.businessUnit.businessUnitDl, service.subBusinessUnit.subBusinessUnitDl]      

        send_email(service, context, cc_email)
        SendNotificationOnTeams(service.teamsChannelWebhookURL
        ,context)

    except Exception as e:
        print(f"email notification exception: {e}")
        raise TypeError("Error sending notification!")    


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
        
@shared_task(bind=True, )
def monitorApiTask(self, serviceId):
    global failed
    global degraded
    try:
        service = get_service(serviceId)
        result = hit_api(service.apiUrl, service.methodType, service.headers, service.requestBody)

        assertion = AssertionAndLimit.objects.get(api=service)

        if result['response_time'] >= assertion.failedResponseTime:
          failed = True
          degraded = False

        elif result['response_time'] >= assertion.degradedResponseTime and result['response_time'] < assertion.degradedResponseTime:
            degraded = True
            failed = False
        else:
            degraded = False
            failed = False

        apiMetrices = APIMetrics.objects.create(
            api = service,
            responseTime = result['response_time'],
            success = result['success'],
            statusCode = result['status'],
            errorMessage = result['error_message'],
            requestStartTime = result['start_time'],
            firstByteTime = result['end_time'],
            responseSize = result['response_size'],
            failed = failed,
            degraded = degraded

        )

        # apiMetrices = APIMetrics.objects.filter(api=service)
        # context = PrepareContext(apiMetrices, service.apiName, service.apiUrl)
        # send_metrics_update(context)
        print(result)
        if result['success']:
            return "Monitored"
        else:
            raise Retry("API call was not successful, retrying...") 

    except Retry as ex:
      try:
        if self.request.retries >= service.maxRetries:

            revokeTask.delay(self.request.id , service.id) 
        
        else:
          SendNotification.delay(service.id, self.request.retries)
          retry_delay =   service.retryAfter
          raise self.retry(exc =ex, countdown = retry_delay) 

      except Exception as notification_error:
        print(f"inside nested exception................... {notification_error}")  

    except ValueError as ex:
       print(ex)

    except AssertionAndLimit.DoesNotExist:
        print("Assertion Does not exist")
    except AssertionAndLimit.MultipleObjectsReturned:
        print('expecting single object...')
    except Exception as ex:
        print(f"Error executing tasks : {ex}")
       

@shared_task
def periodicMonitoring(serviceId):
    try:
        service = get_service(serviceId)

        if service.isApiActive:  
          monitorApiTask.delay(service.id)
 
    except MonitoredAPI.DoesNotExist as e:    
        print( "Wrong service trigerred"  )

    except Exception as e:
        print(f"error scheduling tasks: {e}")   
    
=======
from celery import shared_task

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
>>>>>>> bdd0fb5 (Celery related changes)
