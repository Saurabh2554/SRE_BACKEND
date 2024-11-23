import requests
from operator import attrgetter
from types import SimpleNamespace
from django.utils import timezone
from  graphql import GraphQLError
import json
import xmltodict

def handle_response(response, start_time, end_time):
    try :
        response_time = response.elapsed.total_seconds()
        message = None
        messageList = {}
        parsed_response = {}

        content_type = response.headers.get('Content-Type', '').lower()

        if response.status_code > 400 and response.status_code < 600:
            message = f'{response.reason} :  {response.status_code}' 

        if 'json' in content_type:
            parsed_response = response.json()
            delimiter = "\n"
            
            errors = parsed_response.get('errors', [])
            if errors:
                message_lines = [
                    f"{index + 1} . {error.get('message', 'Unknown error')}"
                    for index, error in enumerate(errors)
                ]
                message = delimiter.join(message_lines)
        # print(f"Error Message : {message}") 
           
        if 'xml' in content_type:
            parsed_response = xmltodict.parse(response.content)
           
            if 'soapenv:Fault' in parsed_response['soapenv:Envelope']['soapenv:Body']:
                FaultObj = parsed_response['soapenv:Envelope']['soapenv:Body']['soapenv:Fault']
        
                if 'faultstring' in FaultObj or 'faultcode' in FaultObj:                 
                  message =  FaultObj['faultstring'] or FaultObj['faultcode']
                else:
                  message = f"Unknow Error, Status : {response.status_code} Occurred !"


        return {
                'status': response.status_code, 
                'response_time': round(float(response_time * 1000), 3) , 
                'error_message':  message, 
                'success':False if message else True,
                'start_time': start_time,
                'end_time':end_time,
                'response_size' : len(response.content),
                }

    except requests.JSONDecodeError as e:
        raise GraphQLError("Invalid JSON Response!")
    except xmltodict.expat.ExpatError as e:
        raise GraphQLError("Invalid XML Response!")
    except Exception as e :
        raise GraphQLError(f"Handle Response Exception : {str(e)}")

def hit_api(api_url, method_type='GET', headers=None, payload=None):
    try:
        response = None
        headers_dict = {}

        if headers:
            headers_dict = {header["key"]: header["value"] for header in headers if header.get("key") and header.get("value")}

        if method_type.upper() in ["GET", "POST"]:
            start_time = timezone.now()
            response = getattr(requests, method_type.lower())(api_url, data = payload, headers=headers_dict)
            end_time = timezone.now()
            
        else:
            raise ValueError("Unsupported Method type. Use 'GET' or 'POST'.")
        return handle_response(response, start_time, end_time)

    except Exception as EX:
        print(f"Some error occurred :: {EX} ")
        raise GraphQLError(f"Some error occurred :: {EX} ")