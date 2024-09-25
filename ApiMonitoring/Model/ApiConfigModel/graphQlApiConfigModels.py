from django.db import models


class GraphQLAPIConfig(models.Model):
    graphql_query = models.TextField()  # Query or mutation for GraphQL API
    
    def __str__(self):
        return f"GraphQL Config (Query: {self.graphql_query[:50]}...)"  # Show first 50 chars of the query


# class GraphQLAPIMetrics(models.Model):
#     graphql_errors = models.JSONField(null=True, blank=True)  # Errors in GraphQL response

#     def __str__(self):
#         return f"GraphQL Metrics (Errors: {self.graphql_errors})"