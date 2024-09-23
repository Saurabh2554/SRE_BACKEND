import requests


class APIError(Exception):
    pass

def hitRestApi(apiUrl, headers=None):
    try:
        response = requests.get(apiUrl, headers = headers)
        response.raise_for_status()
        response_time = response.elapsed.total_seconds()
        
        return {'status': response.status_code, 'response_time':response_time*1000}

    except requests.exceptions.HTTPError as http_error:
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
        message = error_messages.get(response.status_code, "An unknown HTTP error occurred.")
        raise APIError(f"{response.status_code}: {message}")

    except requests.exceptions.RequestException as req_error:
        raise Exception(f"Request failed: {req_error}") 
             