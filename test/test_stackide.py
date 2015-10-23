import unittest
from unittest.mock import Mock, MagicMock, patch
import stack_ide as stackide
from .stubs import sublime
from .fakebackend import FakeBackend
from .mocks import mock_window, cur_dir
from settings import Settings
from .data import status_progress_1
from req import Req

test_settings = Settings("none", [], False)

@patch('stack_ide.stack_ide_loadtargets', return_value=['app/Main.hs', 'src/Lib.hs'])
class StackIDETests(unittest.TestCase):

    def test_can_create(self, loadtargets_mock):
        instance = stackide.StackIDE(
            mock_window([cur_dir + '/mocks/helloworld/']), test_settings, FakeBackend())
        self.assertIsNotNone(instance)
        self.assertTrue(instance.is_active)
        self.assertTrue(instance.is_alive)

        # it got the load targets
        self.assertEqual(2, len(instance.include_targets))

        # it should also have called get source errors,
        # but FakeBackend sends no errors back by default.


    def test_can_send_source_errors_request(self, loadtargets_mock):
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

    def test_handle_welcome_stack_ide_outdated(self, loadtargets_mock):

        backend = MagicMock()
        welcome = {
                  "tag": "ResponseWelcome",
                  "contents": [0, 0, 0]
                  }

        instance = stackide.StackIDE(mock_window([cur_dir + '/projects/helloworld/']), test_settings, backend)
        instance.handle_response(welcome)
        self.assertEqual(sublime.current_error, "Please upgrade stack-ide to a newer version.")


    def test_handle_progress_update(self, loadtargets_mock):
        backend = MagicMock()
        instance = stackide.StackIDE(mock_window([cur_dir + '/projects/helloworld/']), test_settings, backend)
        instance.handle_response(status_progress_1)
        self.assertEqual(sublime.current_status, "Compiling Lib")


    def test_can_shutdown(self, loadtargets_mock):
        backend = FakeBackend()
        backend.send_request = Mock()
        instance = stackide.StackIDE(
            mock_window([cur_dir + '/projects/helloworld/']), test_settings, backend)
        self.assertIsNotNone(instance)
        self.assertTrue(instance.is_active)
        self.assertTrue(instance.is_alive)
        instance.end()
        self.assertFalse(instance.is_active)
        self.assertFalse(instance.is_alive)
        backend.send_request.assert_called_with(
            Req.get_shutdown())

