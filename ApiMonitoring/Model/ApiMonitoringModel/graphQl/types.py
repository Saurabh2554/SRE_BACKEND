import graphene
from graphene_django import DjangoObjectType
from  ..apiMonitorModels import MonitoredAPI 
from .helpers import calculateMetrices, resolve_metrics
from  ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics 

class MoniterApiType(DjangoObjectType):
    class Meta:
      model = MonitoredAPI
      fields = "__all__"

class methodTypeChoice(graphene.ObjectType):
    key = graphene.String()  
    value = graphene.String()

class percentileResponseType(graphene.ObjectType):
   curr_percentile_res_time = graphene.Float()
   percentage_diff = graphene.Float()

class responseTimeType(graphene.ObjectType):
    timestamp = graphene.DateTime()
    responsetime = graphene.Float()
    success = graphene.Boolean()
class validateApiResponse(graphene.ObjectType):
    status = graphene.Int() 
    success = graphene.Boolean()
    message = graphene.String()

class ApiMetricesType(DjangoObjectType):
    class Meta:
        model = MonitoredAPI
        fields = ('id', 'apiName','methodType', 'apiUrl','expectedResponseTime','isApiActive')

    availability_uptime = graphene.Float(name='availability_uptime')
    success_rates = graphene.Float(name='success_rates')
    error_rates = graphene.Float(name='error_rates')
    throughput = graphene.Float(name='throughput')
    avg_latency = graphene.Float(name='avg_latency') 
    downtime = graphene.Float(name='downtime')
    success_count = graphene.Int(name='success_count')
    error_count = graphene.Int(name='error_count')
    avg_response_size = graphene.Float(name='avg_response_size')
    avg_first_byte_time = graphene.Float(name='avg_first_byte_time')
    response_time = graphene.List(responseTimeType, name='response_time')
    percentile_50 = graphene.Field(percentileResponseType, name='percentile_50')  
    percentile_90 = graphene.Field(percentileResponseType, name='percentile_90')  
    percentile_99 = graphene.Field(percentileResponseType, name='percentile_99')  
    last_Error_Occurred = graphene.DateTime()  
    

    def resolve_availability_uptime(self, info):
        return resolve_metrics(self,info)['availability_uptime']

    def resolve_success_rates(self, info):
        return resolve_metrics(self,info)['success_rates']

    def resolve_error_rates(self, info):
        return resolve_metrics(self,info)['error_rates']    

    def resolve_throughput(self, info):
        return resolve_metrics(self,info)['throughput']
    
    def resolve_avg_latency(self, info):
        return resolve_metrics(self,info)['avg_latency']

    def resolve_downtime(self, info):
        return resolve_metrics(self,info)['downtime']

    def resolve_success_count(self, info):
        return resolve_metrics(self,info)['success_count']   

    def resolve_error_count(self, info):
        return resolve_metrics(self,info)['error_count']   

    def resolve_avg_response_size(self, info):
        return resolve_metrics(self,info)['avg_response_size'] 

    def resolve_avg_first_byte_time(self, info):
        return resolve_metrics(self,info)['avg_first_byte_time'] 

    def resolve_response_time(self, info):
        return resolve_metrics(self,info)['response_time']   

    def resolve_percentile_50(self, info):
        return resolve_metrics(self,info)['percentile_50']   
    
    def resolve_percentile_90(self, info):
        return resolve_metrics(self,info)['percentile_90']  
    
    def resolve_percentile_99(self, info):
        return resolve_metrics(self,info)['percentile_99'] 

    def resolve_last_Error_Occured(self, info):
        return resolve_metrics(self,info)['availability_uptime']     

    
#Monitored  Api input values
class MonitoredApiInput(graphene.InputObjectType):
    businessUnit = graphene.UUID(required = True)
    subBusinessUnit = graphene.UUID(required = True)
    apiName = graphene.String()    
    apiUrl = graphene.String()  
    apiCallInterval = graphene.Int()  
    expectedResponseTime = graphene.Int()  
    headers = graphene.String() 
    methodType = graphene.String()
    requestBody = graphene.String()
    recipientDl = graphene.List(graphene.String, required=True)
    createdBy = graphene.String()


