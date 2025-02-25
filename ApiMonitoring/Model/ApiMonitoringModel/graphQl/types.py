import graphene
from graphene_django import DjangoObjectType
from  ..apiMonitorModels import MonitoredAPI 
from .helpers import calculateMetrices, resolve_metrics
from ..assertionAndLimitModels import AssertionAndLimit
from ..schedulingAndAlertingModels import SchedulingAndAlerting
from ..assertionAndLimitResultModels import AssertionAndLimitResult
from ..apiMetricesModels import APIMetrics

class MoniterApiType(DjangoObjectType):
    class Meta:
      model = MonitoredAPI
      fields = "__all__"

class AssertionAndLimitType(graphene.InputObjectType):
    source = graphene.String()
    property = graphene.String(required=False)  # Optional, as per the model with null=True, blank=True
    operator = graphene.String()
    expectedValue = graphene.String()

class SchedulingAndAlertingType(graphene.InputObjectType):
    apiCallInterval = graphene.Int()
    recipientDl = graphene.String()
    createdBy = graphene.String()
    maxRetries = graphene.Int()
    retryAfter = graphene.Int()
    teamsChannelWebhookURL = graphene.String()

class methodTypeChoice(graphene.ObjectType):
    key = graphene.String()  
    value = graphene.String()

class sourceTypeOperatorChoice(graphene.ObjectType):
    source = graphene.String()
    propertyVisibility = graphene.Boolean()
    operators = graphene.List(graphene.String)
class percentileResponseType(graphene.ObjectType):
   curr_percentile_res_time = graphene.Float()
   percentage_diff = graphene.Float()

class SchedulingAndAlertingQueryType(DjangoObjectType):
    class Meta:
        model = SchedulingAndAlerting

class AssertionAndLimitQueryType(DjangoObjectType):
    class Meta:
        model = AssertionAndLimit

class responseTimeType(graphene.ObjectType):
    timestamp = graphene.DateTime()
    responsetime = graphene.Float()
    success = graphene.Boolean()

class validateApiResponse(graphene.ObjectType):
    status = graphene.Int() 
    success = graphene.Boolean()
    message = graphene.String()

class AssertionAndLimitResultType(DjangoObjectType):
    class Meta:
        model = AssertionAndLimitResult
        fields = ("id", "assertion_and_limit", "apimetrics", "actual_value", "status", "timestamp")

class ApiMetricesType(DjangoObjectType):
    class Meta:
        model = MonitoredAPI
        fields = ('id', 'apiName', 'methodType', 'apiUrl', 'isApiActive','assertionAndLimit','schedulingAndAlerting','degradedResponseTime','failedResponseTime')

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
    last_Error_Occurred = graphene.DateTime(name='last_Error_Occurred')

    assertion_results = graphene.List(AssertionAndLimitResultType)

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

    def resolve_last_Error_Occurred(self, info):
        return resolve_metrics(self,info)['last_Error_Occurred']
    
    def resolve_assertion_results(self, info):
        api_metrics = APIMetrics.objects.filter(api=self).values_list('id', flat=True)

        if not api_metrics:
            return []
        
        return AssertionAndLimitResult.objects.filter(apimetrics__id__in=api_metrics)

    
#Monitored  Api input values
class MonitoredApiInput(graphene.InputObjectType):
    businessUnit = graphene.UUID(required=True)
    subBusinessUnit = graphene.UUID(required=True)
    apiName = graphene.String(required=True)
    apiUrl = graphene.String(required=True)
    # assertionAndLimit = graphene.Field(AssertionAndLimitType,required=True)
    assertionAndLimit = graphene.List(AssertionAndLimitType, required=True)
    schedulingAndAlerting = graphene.Field(SchedulingAndAlertingType,required=True)
    headers = graphene.String()
    methodType = graphene.String(required=True)
    requestBody = graphene.String()
    degradedResponseTime = graphene.Int()
    failedResponseTime = graphene.Int()

class MonitoredApiUpdateInput(graphene.InputObjectType):
    assertionAndLimit = graphene.Field(AssertionAndLimitType)
    schedulingAndAlerting = graphene.Field(SchedulingAndAlertingType)
    headers = graphene.String()
    methodType = graphene.String()
    requestBody = graphene.String()



