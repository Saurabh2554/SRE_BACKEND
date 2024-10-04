import requests
from operator import attrgetter
from types import SimpleNamespace
import time
class APIError(Exception):
    pass

def handle_response(response, start_time, end_time):
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
    
    if response.status_code in error_messages:
        message = error_messages[response.status_code]

    return {
            'status': response.status_code, 
            'response_time': response_time * 1000, 
            'error_message':  message, 
            'success':False if message else True,
            'start_time': start_time,
            'end_time':end_time,
            'response_size' : len(response.content),
            }

def hit_api(api_url, api_type='REST', headers=None, payload=None):
    try:
        response = None
        requestStartTime = None
        firstByteTime = None

        if api_type.upper() == 'REST':
            start_time = time.time()
            response = requests.get(api_url, headers=headers)
            end_time = time.time()

        elif api_type.upper() == 'GRAPHQL':
            start_time = time.time()
            response = requests.post(api_url, json=payload, headers = headers)
            end_time = time.time()
     
        else:
            raise ValueError("Unsupported API type. Use 'REST' or 'GRAPHQL'.")
        
        response.raise_for_status()

        print(f"response.header is { len(response.content)}")
        return handle_response(response, start_time, end_time)

    except requests.exceptions.HTTPError as err_msg:
        raise APIError(f"{attrgetter('status', 'error_message','success')(SimpleNamespace(**handle_response(response)))}")

    except requests.exceptions.RequestException as req_error:
        raise Exception(f"Request failed: {req_error}")
