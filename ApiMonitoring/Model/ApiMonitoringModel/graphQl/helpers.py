import math
from graphql import GraphQLError

import math

def calculatePercentile(percentile_rank, response_times):
    # Number of response times
    num_responses = len(response_times)
    
    # Calculate the percentile position (index)
    position = (percentile_rank / 100) * (num_responses + 1)
    
    # Sort the response times
    sorted_times = sorted(response_times)
    
    # Find the value at the floor position (lower bound)
    lower_bound_value = sorted_times[math.floor(position) - 1]
    
    # Find the value at the ceil position (upper bound), handle index out of range
    upper_bound_value = sorted_times[math.ceil(position) - 1] if math.ceil(position) < num_responses else lower_bound_value
    
    # Calculate the percentile using interpolation
    percentile_value = lower_bound_value + (position - math.floor(position)) * (upper_bound_value - lower_bound_value)
    
    return percentile_value


def calculateMetrices(apiMetrices, query_name):
    try:
        total_no_of_requests = apiMetrices.count()
        if total_no_of_requests == 0:
            raise GraphQLError("No data available for the given API.")
 
        # Predefine variables
        availability_uptime = None
        total_successful_requests = 0
        total_failed_requests = 0
        time_difference = None
        latency_per_metrices = []
        response_size_per_metrices = []
        first_byte_time = []
        response_time = []
 
        # Common data fetching for metrics
        if query_name in ['availability_uptime', 'downtime']:
            total_uptime_requests = apiMetrices.filter(statusCode__gte=200, statusCode__lt=400).count()
            availability_uptime = round((total_uptime_requests / total_no_of_requests) * 100, 2)
 
        if query_name in ['success_count', 'success_rates']:
            total_successful_requests = apiMetrices.filter(statusCode=200).count()
 
        if query_name in ['error_count', 'error_rates']:
            total_failed_requests = apiMetrices.filter(statusCode__gte=400, statusCode__lt=600).count()
 
        if query_name in ['throughput', 'downtime']:
            timestamps = apiMetrices.values_list('timestamp', flat=True)
            oldest_timestamps = min(timestamps)
            recent_timestamps = max(timestamps)
            time_difference = (recent_timestamps - oldest_timestamps)
 
        if query_name == 'avg_latency':
            latency_per_metrices = list(apiMetrices.values_list('firstByteTime', 'requestStartTime'))
            latency_per_metrices = [(latency - request_start) for latency, request_start in latency_per_metrices]
 
        if query_name == 'avg_response_size':
            response_size_per_metrices = list(apiMetrices.values_list('responseSize', flat=True))
 
        if query_name == 'avg_first_byte_time':
            first_byte_time = list(apiMetrices.values_list('firstByteTime', flat=True))
 
        if query_name in ['response_time', 'percentile_50', 'percentile_90', 'percentile_99']:
            response_time = list(apiMetrices.values_list('responseTime', flat=True))
 
        # Percentile calculations
        if query_name in ['percentile_50', 'percentile_90', 'percentile_99']:
            percentile_value = int(query_name.split('_')[1])
            currentPercentile = calculatePercentile(percentile_value, response_time)
            previousPercentile = calculatePercentile(percentile_value, response_time[:-1])
            percentageDiff = -1 * (((currentPercentile - previousPercentile) / previousPercentile) * 100)
 
        # Return metrics with calculations
        return {
            'availability_uptime': availability_uptime,
            'success_rates': round((total_successful_requests / total_no_of_requests) * 100, 2) if total_no_of_requests else None,
            'error_rates': round((total_failed_requests / total_no_of_requests) * 100, 2) if total_no_of_requests else None,
            'throughput': round((total_no_of_requests / (time_difference / 60.0)), 3) if time_difference else None,  # requests per minute
            'avg_latency': round(sum(latency_per_metrices) / len(latency_per_metrices), 2) if latency_per_metrices else 0,
            'downtime': round(time_difference * ((100 - availability_uptime) / 100), 2) if availability_uptime < 100 else 0,
            'success_count': total_successful_requests,
            'error_count': total_failed_requests,
            'avg_response_size': round(sum(response_size_per_metrices) / len(response_size_per_metrices), 2) if response_size_per_metrices else 0,
            'avg_first_byte_time': round(sum(first_byte_time) / len(first_byte_time), 2) if first_byte_time else 0,
            'response_time': response_time,
            'percentile_50': {'curr_percentile_res_time': currentPercentile, 'percentage_diff': percentageDiff} if query_name == 'percentile_50' else None,
            'percentile_90': {'curr_percentile_res_time': currentPercentile, 'percentage_diff': percentageDiff} if query_name == 'percentile_90' else None,
            'percentile_99': {'curr_percentile_res_time': currentPercentile, 'percentage_diff': percentageDiff} if query_name == 'percentile_99' else None,
        }
 
    except GraphQLError as gql_error:
        raise gql_error
    except Exception as e:
        raise GraphQLError(f"An error occurred while calculating metrics: {str(e)}")