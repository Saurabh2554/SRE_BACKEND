import graphene

#Utility class to handle success and error formats
# class CustomResponse(graphene.ObjectType):
#     success = graphene.Boolean()
#     code = graphene.String()
#     message = graphene.String()
#     data = graphene.List(graphene.JSONString)  
#     error = graphene.List(graphene.JSONString)  

# class FieldError(graphene.ObjectType):
#     field = graphene.String()  
#     code = graphene.String()   # Error code (e.g. "VALIDATION_ERROR")
#     message = graphene.String()  # Explanation of the error



# # Utility functions to handle success and error responses
# def success_response(data=None, message="Operation successful", code="SUCCESS"):
#     return CustomResponse(
#         success=True,
#         code=code,
#         message=message,
#         data=data,  
#         error=None
#     )


# def error_response(errors=None, message="An error occurred", code="ERROR"):
#     error_list = [FieldError(field=error.get('field', 'unknown'), code=error.get('code', 'UNKNOWN'), message=error.get('message', '')) for error in errors]
#     return CustomResponse(
#         success=False,
#         code=code,
#         message=message,
#         data=None,
#         error=error_list
#     )
