from rest_framework.renderers import JSONRenderer


def response_is_error(response):
    try:
        return response.status_code / 100 in (4, 5)
    except AttributeError:
        return False


class JSONRootObjectRenderer(JSONRenderer):
    media_type = 'application/vnd.rootobject+json'
    format = 'json-rootobject'

    """
    Requires an attribute of 'resource_name' defined in the serializer's Meta class
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = {}
        view = renderer_context.get('view')
        if response_is_error(renderer_context.get('response')):
            response_data = data
        else:
            try:
                resource_name = view.get_serializer().Meta.resource_name
                response_data[resource_name] = data
            except AttributeError:
                response_data = data
        response = super(JSONRootObjectRenderer, self).render(response_data, accepted_media_type, renderer_context)
        return response
