from django.apps import AppConfig


class ApimonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ApiMonitoring'

    def ready(self):
        from .Model.ApiMonitoringModel.graphQl.helpers import CreateMidNightCleanupTask
        CreateMidNightCleanupTask()

