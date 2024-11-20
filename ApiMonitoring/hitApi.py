import requests
from operator import attrgetter
from types import SimpleNamespace
from django.utils import timezone
from  graphql import GraphQLError
import json


def handle_response(response, start_time, end_time, api_type):
    try :
        print(response , start_time, end_time, api_type ,"eeeeeeeeeeeeeee")
        error_messages = {
            400: "Bad Request: The server could not understand the request.",
            401: "Unauthorized: Authentication is required.",
            403: "Forbidden: You do not have permission to access this resource.",
            404: "Not Found: The requested resource was not found.",
            405: "Method Not Allowed: The request method is not supported.",
            408: "Request Timeout: The server timed out waiting for the request.",
            429: "Too Many Requests: You have sent too many requests in a given amount of time.",
            500: "Internal Server Error: The server encountered an unexpected condition.",
            502: "Bad Gateway: Received an invalid response from the upstream server.",
            503: "Service Unavailable: The server is not ready to handle the request."
        }
        response_time = response.elapsed.total_seconds()
        message = None
        messageList = {}
        
        if response.status_code in error_messages:
            message = error_messages[response.status_code]
        
        if api_type.upper() == 'GRAPHQL':
            print(type(response), "lllllllllllllllllllll")

            json_response = response.json()

            print(json_response)
            if 'errors' in json_response and len(json_response['errors']) > 0:
                for index, error_dict in enumerate(json_response['errors']):
                    error_info = {}
                    error_info["message"] = error_dict.get("message")

                    messageList[f"error_{index}"]  = error_info

                message = json.dumps(messageList)


        return {
                'status': response.status_code, 
                'response_time': round(float(response_time * 1000), 3) , 
                'error_message':  message, 
                'success':False if message else True,
                'start_time': start_time,
                'end_time':end_time,
                'response_size' : len(response.content),
                }
    except Exception as e :
        raise GraphQLError(f"Handle Response Exception : {str(e)}")

def hit_api(api_url, api_type='REST', headers=None, payload=None):
    try:
        response = None
        if headers: 
            headers = {header["key"]: header["value"] for header in headers if header["key"] and header["value"]}

        if api_type.upper() == 'REST':
            start_time = timezone.now()
            response = requests.get(api_url, headers=headers)
            end_time = timezone.now()

        elif api_type.upper() == 'GRAPHQL':
            start_time = timezone.now()
            response = requests.post(api_url, json=payload, headers = headers)
            end_time = timezone.now()
     
        else:
            raise ValueError("Unsupported API type. Use 'REST' or 'GRAPHQL'.")

        return handle_response(response, start_time, end_time, api_type)
    
    except Exception as EX:
        print(EX, "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
        raise GraphQLError("Some error occurred")
