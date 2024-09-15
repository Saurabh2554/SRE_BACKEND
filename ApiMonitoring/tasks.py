from celery import shared_task
import requests
from .Model.ApiConfigModel.restApiConfigModels import RestAPIMetrics
from .Model.ApiConfigModel.graphQlApiConfigModels import GraphQLAPIMetrics
from time import sleep


class BaseApiMonitorTask:
    """
    Base class for API monitoring tasks.
    Contains shared functionality for all API types.
    """

    def __init__(self, api_id, api_url, headers, interval):
        self.api_id = api_id
        self.api_url = api_url
        self.headers = headers
        self.interval = interval

    def log_response(self, response, success, error_message=None, specific_metrics=None):
        """
        Log the response from the API and save it to the database.
        """
        # Import here to avoid circular import
        from ApiMonitoring.Model.ApiMonitoringModel.apiMonitorModels import MonitoredAPI
        from ApiMonitoring.Model.ApiMonitoringModel.apiMetricesModels import APIMetrics

        monitored_api = MonitoredAPI.objects.get(id=self.api_id)

        # Create a common metric for the API call
        api_metric = APIMetrics.objects.create(
            api=monitored_api,
            responseTime=response.elapsed.total_seconds() if response else None,
            success=success,
            errorMessage=error_message
        )

        # Save specific metrics for REST or GraphQL
        if isinstance(specific_metrics, RestAPIMetrics):
            api_metric.rest_metrices = specific_metrics
        elif isinstance(specific_metrics, GraphQLAPIMetrics):
            api_metric.graphql_metrices = specific_metrics

        api_metric.save()

        # Update the MonitoredAPI's last known status
        monitored_api.last_status_code = response.status_code if response else None
        monitored_api.save()

    def reschedule_task(self):
        """
        Reschedule the task after the interval defined in `self.interval`.
        """
        monitor_api_task.apply_async(
            kwargs={
                'api_id': self.api_id,
                'api_url': self.api_url,
                'api_type': self.api_type,
                'headers': self.headers,
                'interval': self.interval
            },
            countdown=self.interval
        )


class RestApiMonitorTask(BaseApiMonitorTask):
    """
    Task class to handle REST API monitoring.
    """

    def __init__(self, api_id, api_url, headers, interval):
        super().__init__(api_id, api_url, headers, interval)
        self.api_type = 'REST'

    def call_api(self):
        """
        Call the REST API and log the response.
        """
        try:
            response = requests.get(self.api_url, headers=self.headers)
            # Create a RestAPIMetrics entry
            rest_metrics = RestAPIMetrics.objects.create(
                method='GET',
                status_code=response.status_code
            )
            self.log_response(response, success=response.ok, specific_metrics=rest_metrics)
        except requests.RequestException as e:
            self.log_response(None, success=False, error_message=str(e))

        # Reschedule the task after the interval
        self.reschedule_task()


class GraphqlApiMonitorTask(BaseApiMonitorTask):
    """
    Task class to handle GraphQL API monitoring.
    """

    def __init__(self, api_id, api_url, headers, interval, graphql_query):
        super().__init__(api_id, api_url, headers, interval)
        self.api_type = 'GraphQL'
        self.graphql_query = graphql_query

    def call_api(self):
        """
        Call the GraphQL API and log the response.
        """
        try:
            response = requests.post(self.api_url, headers=self.headers, json={"query": self.graphql_query})
            # Create a GraphQLAPIMetrics entry
            graphql_metrics = GraphQLAPIMetrics.objects.create(
                graphql_query=self.graphql_query
            )
            self.log_response(response, success=response.ok, specific_metrics=graphql_metrics)
        except requests.RequestException as e:
            self.log_response(None, success=False, error_message=str(e))

        # Reschedule the task after the interval
        self.reschedule_task()


# Celery task that acts as a dispatcher
@shared_task
def monitor_api_task(api_id, api_url, api_type, headers, interval, graphql_query=None):
    """
    Celery task that dispatches the appropriate API monitoring task
    based on the API type (REST or GraphQL).
    """
    if api_type == 'REST':
        task = RestApiMonitorTask(api_id, api_url, headers, interval)
    elif api_type == 'GraphQL':
        task = GraphqlApiMonitorTask(api_id, api_url, headers, interval, graphql_query)
    else:
        print(f"Unknown API type: {api_type}")
        return

    # Call the API using the appropriate class method
    task.call_api()
