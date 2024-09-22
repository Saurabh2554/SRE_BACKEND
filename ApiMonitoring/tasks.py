
# from celery import shared_task
# import logging

# from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics
# from ApiMonitoring.Model.ApiConfigModel.restApiConfigModels import RestAPIMetrics
# from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
# from ApiMonitoring.hitApi import hitRestApi
# # Get an instance of a logger
# logger = logging.getLogger(__name__)



# @shared_task
# def monitorApi(apiType, apiUrl, headers, id):
#     try:
#         if apiType == 'REST':
#             try:
#                 result = hitRestApi(apiUrl)

#                 #saving mertices---
#                 monitoredApi = MonitoredApi.objects.get(pk = id)
#                 restApiMetrices = RestAPIMetrics.objects.create(
#                     status_code = response.status_code
#                 )
#                 apiMetrices = APIMetrics.objects.create(
#                      api = monitorApi,
#                      responseTime = response_time,
#                      success = True,
#                      rest_metrices = restApiMetrices
#                 )

#             except requests.exceptions.HttpError as http_error:

            

#          elif apiType == 'GraphQL' :
            
#     except:

    

# @shared_task
# def mul(x, y):
#     return x * y

# @shared_task
# def xsum(numbers):
#     return sum(numbers)