import unittest
from unittest.mock import MagicMock, Mock, ANY
from event_listeners import StackIDESaveListener, StackIDETypeAtCursorHandler, StackIDEAutocompleteHandler
from req import Req
from .stubs.backend import FakeBackend
from .stubs import sublime
from stack_ide import StackIDE
from stack_ide_manager import StackIDEManager
from .mocks import mock_window, mock_view, cur_dir
from settings import Settings
import utility as util

test_settings = Settings("none", [], False)
type_info = "FilePath -> IO String"
span = {
    "spanFromLine": 1,
    "spanFromColumn": 1,
    "spanToLine": 1,
    "spanToColumn": 5
}
exp_types_response = {"tag": "", "contents": [[type_info, span]]}
request_include_targets = {'contents': [{'contents': {'contents': ['src/Main.hs'], 'tag': 'TargetsInclude'}, 'tag': 'RequestUpdateTargets'}], 'tag': 'RequestUpdateSession'}

class ListenerTests(unittest.TestCase):

    def test_requests_update_on_save(self):
        listener = StackIDESaveListener()

        window = mock_window([cur_dir + '/projects/helloworld'])
        view = mock_view('src/Main.hs', window)

        backend = MagicMock()
        backend.send_request = Mock()

        instance = StackIDE(window, test_settings, backend)
        # backend.handler = instance.handle_response

        StackIDEManager.ide_backend_instances[
            window.id()] = instance

        listener.on_post_save(view)
        backend.send_request.assert_any_call(request_include_targets)

    def test_ignores_non_haskell_views(self):
        listener = StackIDESaveListener()

        window = mock_window([cur_dir + '/projects/helloworld'])
        view = mock_view('src/Main.hs', window)
        view.match_selector.return_value = False

        backend = MagicMock()
        backend.send_request = Mock()

        instance = StackIDE(window, test_settings, backend)

        StackIDEManager.ide_backend_instances[
            window.id()] = instance

        listener.on_post_save(view)

        self.assertFalse(backend.send_request.called)

    def test_type_at_cursor_tests(self):
        listener = StackIDETypeAtCursorHandler()

        window = mock_window([cur_dir + '/projects/helloworld'])
        view = mock_view('src/Main.hs', window)

        backend = FakeBackend(exp_types_response)
        instance = StackIDE(window, test_settings, backend)
        backend.handler = instance.handle_response

        StackIDEManager.ide_backend_instances[
            window.id()] = instance

        listener.on_selection_modified(view)
        view.set_status.assert_called_with("type_at_cursor", type_info)
        view.add_regions.assert_called_with("type_at_cursor", ANY, "storage.type", "", sublime.DRAW_OUTLINED)

    def test_request_completions(self):
        window = mock_window([cur_dir + '/projects/helloworld'])
        view = mock_view('src/Main.hs', window)

        listener = StackIDEAutocompleteHandler()
        backend = MagicMock()

        view.settings().get = Mock(return_value=False)
        instance = StackIDE(window, test_settings, backend)
        StackIDEManager.ide_backend_instances[
            window.id()] = instance

        listener.on_query_completions(view, 'm', []) #locations not used.

        req = Req.get_autocompletion(filepath=util.relative_view_file_name(view),prefix="m")
        req['seq'] = ANY

        backend.send_request.assert_called_with(req)
