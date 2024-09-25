# your_project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mySite.settings')

# Create the Celery app instance
app = Celery('mySite')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.enable_utc=False
app.conf.update(timezone='Asia/Kolkata')
# app.conf.beat_schedule = {
#     'monitor-api-1-monthly': {
#         'task': 'your_app.tasks.monitor_api',
#         'schedule': crontab(minute='*/5'),  # Every 5 minutes
#         'args': ('https://api1.example.com',),
#     },
#     'monitor-api-2-monthly': {
#         'task': 'your_app.tasks.monitor_api',
#         'schedule': crontab(minute='*/10'),  # Every 10 minutes
#         'args': ('https://api2.example.com',),
#     },
# }

app.conf.timezone = 'UTC'
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

