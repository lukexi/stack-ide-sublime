import unittest
from unittest.mock import MagicMock, Mock, ANY
from stack_ide_manager import StackIDEManager
import stack_ide as stackide
from .mocks import mock_window, mock_view, cur_dir
from text_commands import ClearErrorPanelCommand, UpdateErrorPanelCommand, ShowHsTypeAtCursorCommand, ShowHsInfoAtCursorCommand, CopyHsTypeAtCursorCommand, GotoDefinitionAtCursorCommand
from .stubs import sublime
from .stubs.backend import FakeBackend
from settings import Settings

type_info = "FilePath -> IO String"
span = {
    "spanFromLine": 1,
    "spanFromColumn": 1,
    "spanToLine": 1,
    "spanToColumn": 5
}
exp_types_response = {"tag": "", "contents": [[type_info, span]]}
someFunc_span_info = {'contents': [[{'contents': {'idProp': {'idDefinedIn': {'moduleName': 'Lib', 'modulePackage': {'packageVersion': None, 'packageName': 'main', 'packageKey': 'main'}}, 'idSpace': 'VarName', 'idType': 'IO ()', 'idDefSpan': {'contents': {'spanFromLine': 9, 'spanFromColumn': 1, 'spanToColumn': 9, 'spanFilePath': 'src/Lib.hs', 'spanToLine': 9}, 'tag': 'ProperSpan'}, 'idName': 'someFunc', 'idHomeModule': None}, 'idScope': {'idImportQual': '', 'idImportedFrom': {'moduleName': 'Lib', 'modulePackage': {'packageVersion': None, 'packageName': 'main', 'packageKey': 'main'}}, 'idImportSpan': {'contents': {'spanFromLine': 3, 'spanFromColumn': 1, 'spanToColumn': 11, 'spanFilePath': 'app/Main.hs', 'spanToLine': 3}, 'tag': 'ProperSpan'}, 'tag': 'Imported'}}, 'tag': 'SpanId'}, {'spanFromLine': 7, 'spanFromColumn': 27, 'spanToColumn': 35, 'spanFilePath': 'app/Main.hs', 'spanToLine': 7}]], 'seq': '724752c9-a7bf-4658-834a-3ff7df64e7e5', 'tag': 'ResponseGetSpanInfo'}
putStrLn_span_info = {'contents': [[{'contents': {'idProp': {'idDefinedIn': {'moduleName': 'System.IO', 'modulePackage': {'packageVersion': '4.8.1.0', 'packageName': 'base', 'packageKey': 'base'}}, 'idSpace': 'VarName', 'idType': 'String -> IO ()', 'idDefSpan': {'contents': '<no location info>', 'tag': 'TextSpan'}, 'idName': 'putStrLn', 'idHomeModule': {'moduleName': 'System.IO', 'modulePackage': {'packageVersion': '4.8.1.0', 'packageName': 'base', 'packageKey': 'base'}}}, 'idScope': {'idImportQual': '', 'idImportedFrom': {'moduleName': 'Prelude', 'modulePackage': {'packageVersion': '4.8.1.0', 'packageName': 'base', 'packageKey': 'base'}}, 'idImportSpan': {'contents': {'spanFromLine': 1, 'spanFromColumn': 8, 'spanToColumn': 12, 'spanFilePath': 'app/Main.hs', 'spanToLine': 1}, 'tag': 'ProperSpan'}, 'tag': 'Imported'}}, 'tag': 'SpanId'}, {'spanFromLine': 7, 'spanFromColumn': 41, 'spanToColumn': 49, 'spanFilePath': 'app/Main.hs', 'spanToLine': 7}]], 'seq': '6ee8d949-82bd-491d-8b79-ffcaa3e65fde', 'tag': 'ResponseGetSpanInfo'}
test_settings = Settings("none", [], False)

class CommandTests(unittest.TestCase):

    def test_can_clear_panel(self):
        cmd = ClearErrorPanelCommand()
        cmd.view = MagicMock()
        cmd.run(None)
        cmd.view.erase.assert_called_with(ANY, ANY)

    def test_can_update_panel(self):
        cmd = UpdateErrorPanelCommand()
        cmd.view = MagicMock()
        cmd.view.size = Mock(return_value=0)
        cmd.run(None, 'message')
        cmd.view.insert.assert_called_with(ANY, 0, "message\n\n")

    def test_can_show_type_at_cursor(self):
        cmd = ShowHsTypeAtCursorCommand()
        window = mock_window([cur_dir + '/projects/helloworld'])
        cmd.view = mock_view('src/Main.hs', window)
        cmd.view.show_popup = Mock()

        backend = FakeBackend(exp_types_response)
        instance = stackide.StackIDE(cmd.view.window(), test_settings, backend)
        backend.handler = instance.handle_response

        StackIDEManager.ide_backend_instances[
            cmd.view.window().id()] = instance

        cmd.run(None)
        cmd.view.show_popup.assert_called_with(type_info)

    def test_can_copy_type_at_cursor(self):
        cmd = CopyHsTypeAtCursorCommand()
        window = mock_window([cur_dir + '/projects/helloworld'])
        cmd.view = mock_view('src/Main.hs', window)

        backend = FakeBackend(exp_types_response)
        instance = stackide.StackIDE(window, test_settings, backend)
        backend.handler = instance.handle_response

        StackIDEManager.ide_backend_instances[
            window.id()] = instance

        cmd.run(None)
        self.assertEqual(sublime.clipboard, type_info)

    def test_can_request_show_info_at_cursor(self):
        cmd = ShowHsInfoAtCursorCommand()
        window = mock_window([cur_dir + '/projects/helloworld'])
        cmd.view = mock_view('src/Main.hs', window)
        cmd.view.show_popup = Mock()

        backend = FakeBackend(someFunc_span_info)
        instance = stackide.StackIDE(cmd.view.window(), test_settings, backend)
        backend.handler = instance.handle_response

        StackIDEManager.ide_backend_instances[
            window.id()] = instance

        cmd.run(None)
        cmd.view.show_popup.assert_called_with("someFunc :: IO ()  (Defined in src/Lib.hs:9:1)")

    def test_show_info_from_module(self):
        cmd = ShowHsInfoAtCursorCommand()
        window = mock_window([cur_dir + '/projects/helloworld'])
        cmd.view = mock_view('src/Main.hs', window)
        cmd.view.show_popup = Mock()

        backend = FakeBackend(putStrLn_span_info)
        instance = stackide.StackIDE(cmd.view.window(), test_settings, backend)
        backend.handler = instance.handle_response

        StackIDEManager.ide_backend_instances[
            window.id()] = instance

        cmd.run(None)
        cmd.view.show_popup.assert_called_with("putStrLn :: String -> IO ()  (Imported from Prelude)")

    def test_goto_definition_at_cursor(self):
        global cur_dir
        cmd = GotoDefinitionAtCursorCommand()
        window = mock_window([cur_dir + '/projects/helloworld'])
        window.open_file = Mock()
        cmd.view = mock_view('src/Main.hs', window)

        backend = FakeBackend(someFunc_span_info)
        instance = stackide.StackIDE(cmd.view.window(), test_settings, backend)
        backend.handler = instance.handle_response

        StackIDEManager.ide_backend_instances[
            window.id()] = instance

        cmd.run(None)
        window.open_file.assert_called_with(cur_dir + "/projects/helloworld/src/Lib.hs:9:1", sublime.ENCODED_POSITION)

    def test_goto_definition_of_module(self):
        global cur_dir
        cmd = GotoDefinitionAtCursorCommand()
        window = mock_window([cur_dir + '/projects/helloworld'])
        cmd.view = mock_view('src/Main.hs', window)
        window.status_message = Mock()
        cmd._handle_response(putStrLn_span_info.get('contents'))
        self.assertEqual("Cannot navigate to putStrLn, it is imported from Prelude", sublime.current_status)
