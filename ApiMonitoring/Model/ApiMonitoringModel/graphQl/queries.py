import graphene
from  ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI 
from ApiMonitoring.hitApi import hit_api
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
    validate_api = graphene.Field(validateApiResponse, 
    apiUrl = graphene.String(required=True),
    apiType = graphene.String(required = True), 
    query = graphene.String(),
    headers = graphene.String()
    )

    def resolve_api_type_choices(self, info, **kwargs): 
        choices = MonitoredAPI.API_TYPE_CHOICES
        return [
            {'key': key, 'value': value} for key, value in choices
        ]

    def resolve_validate_api(self, info, apiUrl, apiType, query=None, headers=None):
        try:
            result = None
            if apiType == 'REST':

                headers_dict = json.loads(headers) if headers else {}
                result =  hit_api(apiUrl,apiType, headers_dict) 

            elif apiType == 'GraphQL' :
                
                payload = {
                    'query': query
                }
                
                result = hit_api(apiUrl, apiType, headers, payload)

            return validateApiResponse(status = result['status'], response_time = result['response_time'])    

        except Exception as e:
          raise GraphQLError(f"{str(e)}")
        



