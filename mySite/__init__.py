from __future__ import absolute_import, unicode_literals
from .celery import app as SRE_CELERY_APP

__all__ = ('SRE_CELERY_APP')
import requests

# #https://qa.api.data-axle.com/v1/lookups/yellow_page_codes/download
# #https://rickandmortyapi.com/api/character/70
# try:
#     response = requests.get('https://rickandmortyapi.com/api/character/70')
#     print(f"response.content is  : {response.content}")
#     print(f"response.json is  : {response.json}")
#     print(f"response.headers is  : {response.headers}")
#     response.raise_for_status()
#     response_time = response.elapsed.total_seconds()
#     for key, value in response.__dict__.items():
#         print(f"{key}: {value}")
# except requess.exceptions.HTTPError as http_error:  
#     print(f"error is {http_error}")      