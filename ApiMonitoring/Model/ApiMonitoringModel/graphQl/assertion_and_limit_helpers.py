from ApiMonitoring.Model.ApiMonitoringModel.graphQl.helpers import (
    get_service, get_metrices, get_assertions_for_service
)
from ApiMonitoring.Model.ApiMonitoringModel.assertionAndLimitResultModels import AssertionAndLimitResult
from graphql import GraphQLError
from jsonpath_ng import parse
from jsonpath_ng.exceptions import JsonPathLexerError
import decimal
import re

SOURCE_CHOICES = {
    'status_code': 'Status Code',
    'headers': 'Headers',
    'json_body': 'JSON Body'
}

VALID_OPERATORS = {
        'status_code': ['equals', 'not_equals', 'greater_than', 'less_than'],
        'headers': ['equals', 'not_equals', 'is_empty', 'is_not_empty', 'greater_than', 'less_than', 'contains', 'not_contains'],
        'json_body': ['equals', 'not_equals', 'is_empty', 'is_not_empty', 'greater_than', 'less_than', 'contains', 'not_contains', 'is_null','is_not_null']
    }


ALLOW_PROPERTY = {
    'headers': True,  
    'json_body': True,  
    'status_code': False
    }


def getValueFromJSON(json_data, json_path):
    """Extracts values from JSON using a JsonPath expression."""
    try:
        jsonpath_expr = parse(json_path)
        matches = jsonpath_expr.find(json_data)
        return [m.value for m in matches] if matches else None
    except JsonPathLexerError:
        raise GraphQLError(f"Invalid JsonPath Syntax: {json_path}")
    except Exception as e:
        raise GraphQLError(f"Unexpected error while processing JSONPath '{json_path}': {e}")

def try_convert(value, target_type):
    """Attempts to convert a value to the target type."""
    try:
        if target_type is bool:
            return str(value).strip().lower() == "true"
        if target_type is decimal.Decimal:
            return decimal.Decimal(value)
        return target_type(value)
    except (ValueError, TypeError, decimal.InvalidOperation):
        return None

def checkAssertion(serviceId, metriceId, response):
    """Validates API response assertions against stored rules."""
    # service = get_service(serviceId=serviceId)
    metrices = get_metrices(metriceId=metriceId)
    assertions = get_assertions_for_service(serviceId=serviceId)

    for assertion in assertions:
        actual_value = None
        status = False  # Default status

        # Status Code Assertions
        if assertion.source == "status_code":
            actual_value = metrices.statusCode
            expected = int(assertion.expectedValue) if assertion.expectedValue is not None else None

            if expected is not None:
                comparison_operators = {
                    "equals": actual_value == expected,
                    "not_equals": actual_value != expected,
                    "greater_than": actual_value > expected,
                    "less_than": actual_value < expected,
                }
                status = comparison_operators.get(assertion.operator, False)

        # JSON Body Assertions
        elif assertion.source == "json_body":
            content_type = response.headers.get("Content-Type", "").lower()
            if "json" in content_type:
                try:
                    parsed_response = response.json()
                    extracted_values = getValueFromJSON(parsed_response, assertion.property)
                except Exception as e:
                    raise GraphQLError(f"Failed to parse JSON response: {e}")

                expected_value = assertion.expectedValue
                operator = assertion.operator

                if extracted_values:
                    for extracted_value in extracted_values:
                        converted_expected = try_convert(expected_value, type(extracted_value))  # Fixed here

                        # Boolean condition map
                        condition_map = {
                            "equals": extracted_value == converted_expected,
                            "not_equals": extracted_value != converted_expected,
                            "greater_than": converted_expected is not None and extracted_value > converted_expected,
                            "less_than": converted_expected is not None and extracted_value < converted_expected,
                            "contains": str(expected_value) in str(extracted_value),
                            "not_contains": str(expected_value) not in str(extracted_value),
                            "is_empty": extracted_value in ["", None],
                            "is_not_empty": extracted_value not in ["", None],
                            "is_null": extracted_value is None,
                            "is_not_null": extracted_value is not None,
                        }

                        if condition_map.get(operator, False):
                            status = True
                            actual_value = extracted_value
                            break 
                        else:
                            actual_value = extracted_value

        elif assertion.source == 'headers':
            
            operator = assertion.operator
            actual_value = response.headers.get(assertion.property,None)

            if actual_value is not None and assertion.regex:
                match = re.search(assertion.regex, actual_value)
                if match:
                    actual_value = match.group(1)
                else:
                    actual_value = None
            
            if actual_value is not None:
                converted_expected = try_convert(assertion.expectedValue, type(actual_value))

                condition_map = {
                    "equals": actual_value == converted_expected,
                    "not_equals": actual_value != converted_expected,
                    "greater_than": converted_expected is not None and actual_value > converted_expected,
                    "less_than" : converted_expected is not None and actual_value < converted_expected,
                    "contains" : assertion.expectedValue in str(actual_value),
                    "not_contains" : assertion.expectedValue not in str(actual_value),
                    "is_empty" : actual_value in ["",None],
                    "is_not_empty" : actual_value not in ["", None],
                    "is_null" : actual_value is None,
                    "is_not_null" : actual_value is not None,
                }
            if condition_map.get(operator,False):
                status = True
                            

        # Store assertion result
        assertion_result = AssertionAndLimitResult.objects.create(
            assertion_and_limit=assertion,
            apimetrics=metrices,
            actual_value=actual_value,
            status=status
        )

        print(f"Assertion Result: {assertion_result}")

