import json

from django.conf import settings
from django.http import Http404, JsonResponse
from watchman import settings as watchman_settings, views as watchman_views

from caluma.caluma_user.models import AnonymousUser


def _remove_keys(dictionary, keys):
    """Recursively remove given keys from dictionary."""
    for key in keys:  # delete keys
        if key in dictionary:
            del dictionary[key]
    for value in dictionary.values():  # retrieve nested values
        if isinstance(value, dict):
            _remove_keys(value, keys)  # apply to dict
        if isinstance(value, list):
            [_remove_keys(v, keys) for v in value]  # apply to list


def health_check_status(request):
    """Modify django-watchman view to remove error / stacktrace output.

    Available django-watchman views:
    watchman.views.status
    watchman.views.bare_status
    """
    # if health endpoint not enabled, return 404 response
    if not settings.ENABLE_HEALTHZ_ENDPOINT:
        raise Http404("Healthz endpoint not enabled.")

    # set anonymous user for requests to health endpoint
    # caluma expects user to be set on requests
    request.user = AnonymousUser()

    # Get view response from django-watchman
    response = watchman_views.status(request)
    json_data = json.loads(response.content.decode("utf-8"))

    # Remove unwanted keys e.g. 'error', 'stacktrace'
    if response.status_code == watchman_settings.WATCHMAN_ERROR_CODE:
        _remove_keys(json_data, ["error", "stacktrace"])
        return JsonResponse(json_data, status=response.status_code)

    return response
