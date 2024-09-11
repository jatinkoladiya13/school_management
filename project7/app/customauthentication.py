from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from .models import User
from bson import ObjectId
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.exceptions import  TokenError
from rest_framework_simplejwt.state import token_backend


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
            tokenso = OutstandingToken.objects.get(user_id=str(user_id))

            if tokenso is not None:
                raise exceptions.AuthenticationFailed(_('Blacklist token is not valid.'))

        except  ObjectDoesNotExist:
            pass


        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise exceptions.AuthenticationFailed(_('Token contained no recognizable user identification'))

        try:
    
            token_str = str(validated_token)
            token_data = token_backend.decode(token_str, verify=True)
        except TokenError:
            raise exceptions.AuthenticationFailed(_('Invalid token'))

        try:
            user = User.objects.get(_id=ObjectId(user_id))
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('User not found'))

        return user