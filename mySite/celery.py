# your_project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.beat import crontab


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mySite.settings')

# Create the Celery app instance
app = Celery('mySite')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.enable_utc=False
app.conf.update(timezone='Asia/Kolkata')

def setScheduleTasks(apiName, min, serviceId):
   app.conf.beat_schedule = {
    f'monitor-api_{apiName}': {
        'task': 'ApiMonitoring.tasks.periodicMonitoring',
        'schedule': crontab(minute=f'*/{min}'),
        'args':(serviceId) 
    },
  }

app.autodiscover_tasks()
app.conf.timezone = 'UTC'
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

