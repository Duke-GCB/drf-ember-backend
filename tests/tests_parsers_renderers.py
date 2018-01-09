from six import StringIO
import json

from django.test import TestCase
from mock import MagicMock

from drf_ember_backend.parsers import JSONRootObjectParser, ParseError
from drf_ember_backend.renderers import JSONRootObjectRenderer


class ParserRendererTestCase(TestCase):

    def setUp(self):
        # Configure mock parser_context
        mock_view = MagicMock()
        serializer = MagicMock()
        self.mock_serializer = serializer
        serializer.Meta = MagicMock(resource_name='objects')
        mock_view.get_serializer = MagicMock(return_value=serializer)
        self.parser_context = {'view': mock_view}
        self.renderer_context = {'view': mock_view}


class JSONRootObjectRendererTestCase(ParserRendererTestCase):

    def setUp(self):
        super(JSONRootObjectRendererTestCase, self).setUp()
        self.renderer = JSONRootObjectRenderer()
        self.data = [{'size': 'medium'}, {'size': 'large'}]
        self.wrapped = {'objects': self.data}

    def _render(self):
        return self.renderer.render(self.data, self.renderer.media_type, self.renderer_context)

    def test_renders_resource(self):
        self.assertTrue(hasattr(self.mock_serializer.Meta, 'resource_name'))
        rendered = self._render()
        self.assertEqual(json.loads(rendered), self.wrapped)

    def test_renders_without_wrapper_when_no_resource_name(self):
        delattr(self.mock_serializer.Meta, 'resource_name')
        self.assertFalse(hasattr(self.mock_serializer.Meta, 'resource_name'))
        rendered = self._render()
        self.assertEqual(json.loads(rendered), self.data)

    def test_media_type(self):
        self.assertEqual(self.renderer.media_type, 'application/vnd.rootobject+json')

    def test_renders_without_wrapper_when_error(self):
        self.renderer_context['response'] = MagicMock(status_code=404)
        rendered = self._render()
        self.assertEqual(json.loads(rendered), self.data)

        self.renderer_context['response'] = MagicMock(status_code=500)
        rendered = self._render()
        self.assertEqual(json.loads(rendered), self.data)


class JSONRootObjectParserTestCase(ParserRendererTestCase):

    def setUp(self):
        super(JSONRootObjectParserTestCase, self).setUp()
        self.parser = JSONRootObjectParser()
        self.object = {'objects': {'size': 'medium'}}
        self.json = json.dumps(self.object)

    def _parse(self):
        return self.parser.parse(StringIO(self.json), JSONRootObjectParser.media_type, self.parser_context)

    def test_parses_resource(self):
        self.assertTrue(hasattr(self.mock_serializer.Meta, 'resource_name'))
        parsed = self._parse()
        self.assertEqual(parsed, self.object['objects'])

    def test_raises_parse_error_when_no_resource_name(self):
        delattr(self.mock_serializer.Meta, 'resource_name')
        self.assertFalse(hasattr(self.mock_serializer.Meta, 'resource_name'))
        with self.assertRaises(ParseError):
            self._parse()

    def test_raises_key_error(self):
        self.mock_serializer.Meta = MagicMock(resource_name='others')
        self.assertTrue(hasattr(self.mock_serializer.Meta, 'resource_name'))
        with self.assertRaises(ParseError):
            self._parse()

    def test_media_type(self):
        self.assertEqual(self.parser.media_type, 'application/vnd.rootobject+json')
