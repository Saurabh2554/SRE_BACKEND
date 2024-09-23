import graphene
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI 
from ApiMonitoring.hitApi import hitRestApi
from graphql import GraphQLError
import json


class apiTypeChoice(graphene.ObjectType):
    key = graphene.String()  
    value = graphene.String()

class validateApiResponse(graphene.ObjectType):
    status = graphene.Int() 
    response_time = graphene.Float()


class Query(graphene.ObjectType):
    api_type_choices = graphene.List(apiTypeChoice)
    validate_api = graphene.Field(validateApiResponse, apiUrl = graphene.String(required=True),headers = graphene.String())

    def resolve_api_type_choices(self, info, **kwargs): 
        choices = MonitoredAPI.API_TYPE_CHOICES
        return [
            {'key': key, 'value': value} for key, value in choices
        ]

    def resolve_validate_api(self, info, apiUrl,headers):
        try:
            
            headers_dict = json.loads(headers) if headers else {}
            result =  hitRestApi(apiUrl, headers_dict)

            return validateApiResponse(status = result['status'], response_time = result['response_time'])
            
        except Exception as e:
            raise GraphQLError(f"{str(e)}")
        



