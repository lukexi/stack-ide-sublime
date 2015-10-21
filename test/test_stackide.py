import unittest
from unittest.mock import Mock, MagicMock
import stack_ide as stackide
from .stubs import sublime
from .stubs.backend import FakeBackend
from .mocks import mock_window, cur_dir
from settings import Settings
from req import Req

test_settings = Settings("none", [], False)


class StackIDETests(unittest.TestCase):

    def test_can_create(self):
        instance = stackide.StackIDE(
            mock_window([cur_dir + '/mocks/helloworld/']), test_settings, FakeBackend())
        self.assertIsNotNone(instance)
        self.assertTrue(instance.is_active)
        self.assertTrue(instance.is_alive)

    def test_can_send_source_errors_request(self):
        backend = FakeBackend()
        backend.send_request = Mock()
        instance = stackide.StackIDE(
            mock_window([cur_dir + '/mocks/helloworld/']), test_settings, backend)
        self.assertIsNotNone(instance)
        self.assertTrue(instance.is_active)
        self.assertTrue(instance.is_alive)
        req = Req.get_source_errors()
        instance.send_request(req)
        backend.send_request.assert_called_with(req)

    def test_handle_welcome_stack_ide_outdated(self):

        backend = MagicMock()
        welcome = {
                  "tag": "ResponseWelcome",
                  "contents": [0, 0, 0]
                  }

        instance = stackide.StackIDE(mock_window([cur_dir + '/mocks/helloworld/']), test_settings, backend)
        instance.handle_response(welcome)
        self.assertEqual(sublime.current_error, "Please upgrade stack-ide to a newer version.")


    def test_can_shutdown(self):
        backend = FakeBackend()
        backend.send_request = Mock()
        instance = stackide.StackIDE(
            mock_window([cur_dir + '/mocks/helloworld/']), test_settings, backend)
        self.assertIsNotNone(instance)
        self.assertTrue(instance.is_active)
        self.assertTrue(instance.is_alive)
        instance.end()
        self.assertFalse(instance.is_active)
        self.assertFalse(instance.is_alive)
        backend.send_request.assert_called_with(
            Req.get_shutdown())

