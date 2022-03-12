from django.core.exceptions import PermissionDenied, ValidationError
from django.http.response import Http404
from django_fsm import TransitionNotAllowed
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.views import set_rollback


def handle_drf_exception(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, (PermissionDenied, TransitionNotAllowed)):
        exc = exceptions.PermissionDenied()
    elif isinstance(exc, ValidationError):
        exc = exceptions.ValidationError(detail=serializers.as_serializer_error(exc))

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = exc.get_full_details()
        else:
            data = {"detail": exc.get_full_details()}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return None
