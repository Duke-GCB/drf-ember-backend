from rest_framework.views import exception_handler
from drf_ember_backend.renderers import JSONRootObjectRenderer

SOURCE_POINTER_PREFIX = '/data/attributes'


def switching_exception_handler(exc, context):
    request = context.get('request')
    handler = exception_handler
    if request.accepted_media_type == JSONRootObjectRenderer.media_type:
        handler = json_root_object_exception_handler
    return handler(exc, context)


def make_json_root_error(status_code, data, exc):
    # JSON root errors should conform to JSONAPI: http://jsonapi.org/format/#error-objects
    error = { 'status': status_code }
    if isinstance(data, str):
        error['detail'] = data
    elif isinstance(data, dict):
        if 'detail' in data:
            error['detail'] = data['detail']
        else:
            for key in data.keys():
                value = data[key]
                error['source'] = {
                    'pointer': '{}/{}'.format(SOURCE_POINTER_PREFIX, key)
                }
                error['detail'] = value
        if 'id' in data:
            error['id'] = data.get('id')
    return error


def json_root_object_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # If exception_handler returns None, the exception has not been handled by rest_framework
    # If we return None, Django responds with a 500 (and html in debug mode). So we should handle them and
    # return appropriate responses. For now, we'll just return None from the handler to aid ongoing development
    if response is None:
        return None
    # response.data may be list or a single object
    if isinstance(response.data, list):
        errors = [make_json_root_error(response.status_code, data, exc) for data in response.data]
    else:
        errors = [make_json_root_error(response.status_code, response.data, exc)]

    response.data = {'errors': errors}
    return response
