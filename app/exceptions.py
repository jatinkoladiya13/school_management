from rest_framework.views  import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import exceptions


def custom_exception_handler(exc,context):
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(exc, exceptions.AuthenticationFailed):
            response.data = {
                'status': response.status_code,
                'detail': str(exc),
                'code': 'authentication_failed'
            }
        elif isinstance(exc,(TokenError, InvalidToken)):
         return Response(
            {
                "status":"400",
                "detail": "Given token not valid for any token type",
                "code": "token_not_valid",
                "messages": [
                    {
                        "token_class": exc.__class__.__name__,
                        "token_type": "access", 
                        "message": str(exc)
                    }
                ]
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        else:
            response = Response(
                {
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'detail': str(exc),
                    'code': 'unknown_error'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return response    