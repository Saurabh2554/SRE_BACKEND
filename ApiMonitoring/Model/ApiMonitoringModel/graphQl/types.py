import graphene
from graphene_django import DjangoObjectType
from  ..apiMonitorModels import MonitoredAPI 
from .helpers import calculateMetrices
from  ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics 

class MoniterApiType(DjangoObjectType):
    class Meta:
      model = MonitoredAPI
      fields = "__all__"

class apiTypeChoice(graphene.ObjectType):
    key = graphene.String()  
    value = graphene.String()

class percentileResponseType(graphene.ObjectType):
   key = graphene.String()
   value = graphene.Float()

class validateApiResponse(graphene.ObjectType):
    status = graphene.Int() 
    success = graphene.Boolean()

class ApiMetricesType(DjangoObjectType):
    class Meta:
        model = MonitoredAPI
        fields = ('id', 'apiName','apiType', 'apiUrl','expectedResponseTime')

    availability_uptime = graphene.Float()
    success_rates = graphene.Float()
    error_rates = graphene.Float()
    throughput = graphene.Float()
    avg_latency =graphene.Float() 
    downtime = graphene.Float()
    success_count = graphene.Int()
    error_count = graphene.Int()
    avg_response_size = graphene.Float()
    avg_first_byte_time = graphene.Float()
    response_time = graphene.List(graphene.Float)
    percentile_50 = graphene.Field(percentileResponseType)  
    percentile_90 = graphene.Field(percentileResponseType)  
    percentile_99 = graphene.Field(percentileResponseType)  


    def resolve_metrics(self, info):
        metrics = calculateMetrices(APIMetrics.objects.filter(api=self).order_by('timestamp'), info.field_name)
        return metrics

    def resolve_availability_uptime(self, info):
        return self.resolve_metrics(info)['availability_uptime']

    def resolve_success_rates(self, info):
        return self.resolve_metrics(info)['success_rates']

    def resolve_error_rates(self, info):
        return self.resolve_metrics(info)['error_rates']    

    def resolve_throughput(self, info):
        return self.resolve_metrics(info)['throughput']
    
    def resolve_avg_latency(self, info):
        return self.resolve_metrics(info)['avg_latency']

    def resolve_downtime(self, info):
        return self.resolve_metrics(info)['downtime']

    def resolve_success_count(self, info):
        return self.resolve_metrics(info)['success_count']   

    def resolve_error_count(self, info):
        return self.resolve_metrics(info)['error_count']   

    def resolve_avg_response_size(self, info):
        return self.resolve_metrics(info)['avg_response_size'] 

    def resolve_avg_first_byte_time(self, info):
        return self.resolve_metrics(info)['avg_first_byte_time'] 

    def resolve_response_time(self, info):
        return self.resolve_metrics(info)['response_time']   

    def resolve_percentile_50(self, info):
        return self.resolve_metrics(info)['percentile_50']   
    
    def resolve_percentile_90(self, info):
        return self.resolve_metrics(info)['percentile_90']  
    
    def resolve_percentile_99(self, info):
        return self.resolve_metrics(info)['percentile_99']  

#Monitored  Api input values
class MonitoredApiInput(graphene.InputObjectType):
    businessUnit = graphene.UUID(required = True)
    subBusinessUnit = graphene.UUID(required = True)
    apiName = graphene.String()  
    apiType = graphene.String()  
    apiUrl = graphene.String()  
    apiCallInterval = graphene.Int()  
    expectedResponseTime = graphene.Int()  
    headers = graphene.JSONString() 
    graphqlQuery = graphene.String()
    recipientDl = graphene.String()
    createdBy = graphene.String()