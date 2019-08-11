from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer


def success(data=None):
    return get_json_response_object(True, '200', data)


def not_supported():
    return get_json_response_object(False, '501', None)


def action_failed():
    return get_json_response_object(False, '400', None)


def get_json_response_object(is_ok, status, data):
    return HttpResponse(get_response_object(is_ok, data), content_type='application/json', status=status)


def get_response_object(is_ok, data=None):
    return JSONRenderer().render({
        'isOk': is_ok,
        'data': data
    })
