from rest_framework.parsers import JSONParser, ParseError
from drf_ember_backend.renderers import JSONRootObjectRenderer
import six


class JSONRootObjectParser(JSONParser):
    """
    A parser that expects incoming content to be wrapped in a root object for compatibility with
    Ember's DS.RESTAdapter. The root key should match a resource_name on a serializer's Meta class

    Example:

    {
        "users": {
            "name": "Ben Franklin",
            "email": "bfranklin@usa.gov"
        }
    }

    """
    media_type = 'application/vnd.rootobject+json'
    renderer_class = JSONRootObjectRenderer

    def parse(self, stream, media_type=None, parser_context=None):
        parsed = super(JSONRootObjectParser, self).parse(stream, media_type, parser_context)
        view = parser_context.get('view')
        try:
            # Check that the serializer for the given route matches the resource name in the parsed data
            resource_name = view.get_serializer().Meta.resource_name
        except AttributeError as exc:
            # When our serializer object has no resource name we don't know what to expect.
            raise ParseError('JSON parse error - %s' % six.text_type(exc))
        try:
            return parsed[resource_name]
        except KeyError as exc:
            # When our resource_name is defined but not found in the data, we should not try to extract it
            raise ParseError('JSON parse error - %s' % six.text_type(exc))

