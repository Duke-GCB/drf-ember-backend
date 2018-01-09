from django.test import TestCase
from mock import Mock, MagicMock, patch
from drf_ember_backend.exception_handlers import *


class SwitchingExceptionHandlerTestCase(TestCase):

    @patch('drf_ember_backend.exception_handlers.json_root_object_exception_handler')
    def test_uses_handler_for_json_root_media_type(self, mock_handler):
        context = {'request': MagicMock(accepted_media_type=JSONRootObjectRenderer.media_type)}
        switching_exception_handler(None, context)
        self.assertTrue(mock_handler.called,
                        'When content is JSONRootObject, should call json_root_object_exception_handler')

    @patch('drf_ember_backend.exception_handlers.exception_handler')
    def test_uses_base_handler_by_default(self, mock_handler):
        context = {'request': MagicMock(accepted_media_type='text/plain')}
        switching_exception_handler(None, context)
        self.assertTrue(mock_handler.called, 'When not JSONRootObject, should call exception_handler')


class MakeJsonRootErrorTestCase(TestCase):

    def test_makes_error_object_from_dict_with_detail(self):
        status_code = 401
        exc = MagicMock()
        data = {'detail': 'Detail message', 'id': 6}
        error = make_json_root_error(status_code, data, exc)
        self.assertEqual(error['status'], status_code, 'JSON root error should contain the status code')
        self.assertEqual(error['detail'], 'Detail message',
                         'JSON root error should use the data detail as the detail message')
        self.assertEqual(error['id'], 6, 'With a dict containing id, JSON root error should include this id')

    def test_makes_error_object_from_dict_with_field_keys(self):
        status_code = 400
        exc = MagicMock()
        data = {'jobName': 'Some value'}
        error = make_json_root_error(status_code, data, exc)
        self.assertEqual(error['status'], status_code, 'JSON root error should contain the status code')
        self.assertEqual(error['detail'], 'Some value',
                         'JSON root error should use the key values as the detail message')
        self.assertEqual(error['source'], {'pointer': '/data/attributes/jobName'})

    def test_makes_error_object_from_str(self):
        status_code = 401
        exc = MagicMock()
        data = 'Detail message'
        error = make_json_root_error(status_code, data, exc)
        self.assertEqual(error['status'], status_code, 'JSON root error should contain the status code')
        self.assertEqual(error['detail'], 'Detail message', 'JSON root error should use a str as the detail message')
        self.assertNotIn('id', error, 'With str data, JSON root error should not contain an id field')


class JsonRootObjectExceptionHandlerTestCase(TestCase):

    def setUp(self):
        self.exc = Mock()
        self.context = Mock()
        self.error = Mock()

    @patch('drf_ember_backend.exception_handlers.exception_handler')
    @patch('drf_ember_backend.exception_handlers.make_json_root_error')
    def test_calls_base_exception_handler(self, mock_make_json_root_error, mock_exception_handler):
        response = json_root_object_exception_handler(self.exc, self.context)
        self.assertTrue(mock_exception_handler.called_with(self.exc, self.context),
                        'Should call the base exception handler with provided arguments')
        self.assertTrue(mock_make_json_root_error.called,
                        'Should call make_json_root_error')

    @patch('drf_ember_backend.exception_handlers.exception_handler')
    @patch('drf_ember_backend.exception_handlers.make_json_root_error')
    def test_makes_errors_from_list(self, mock_make_json_root_error, mock_exception_handler):
        data = ['a','b','c']
        mock_exception_handler.return_value = MagicMock(data=data)
        mock_make_json_root_error.return_value = self.error
        response = json_root_object_exception_handler(self.exc, self.context)
        self.assertEqual(mock_make_json_root_error.call_count, 3,
                         'Should call make_json_root_error 3 for each item in data')
        self.assertEqual(response.data, {'errors': [self.error, self.error, self.error]},
                         'response.data should be a dictionary containing list of 3 errors')

    @patch('drf_ember_backend.exception_handlers.exception_handler')
    @patch('drf_ember_backend.exception_handlers.make_json_root_error')
    def test_makes_errors_from_dict(self, mock_make_json_root_error, mock_exception_handler):
        data = {}
        mock_exception_handler.return_value = MagicMock(data=data)
        mock_make_json_root_error.return_value = self.error
        response = json_root_object_exception_handler(self.exc, self.context)
        self.assertEqual(mock_make_json_root_error.call_count, 1,
                         'Should call make_json_root_error once for a dictionary in data')
        self.assertEqual(response.data, {'errors': [self.error]},
                         'response.data should be a dictionary containing list of 1 error')
