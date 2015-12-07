import unittest
from unittest.mock import MagicMock, Mock, ANY
import stack_ide as stackide
from .mocks import cur_dir, default_mock_window, setup_fake_backend
from text_commands import ClearErrorPanelCommand, AppendToErrorPanelCommand, ShowHsTypeAtCursorCommand, ShowHsInfoAtCursorCommand, CopyHsTypeAtCursorCommand, GotoDefinitionAtCursorCommand
from .stubs import sublime
from .data import type_info, someFunc_span_info, putStrLn_span_info


class CommandTests(unittest.TestCase):

    def setUp(self):
        stackide.stack_ide_loadtargets = Mock(return_value=['app/Main.hs', 'src/Lib.hs'])

    def test_can_clear_panel(self):
        cmd = ClearErrorPanelCommand()
        cmd.view = MagicMock()
        cmd.run(None)
        cmd.view.erase.assert_called_with(ANY, ANY)

    def test_can_update_panel(self):
        cmd = AppendToErrorPanelCommand()
        cmd.view = MagicMock()
        cmd.view.size = Mock(return_value=0)
        cmd.run(None, 'message')
        cmd.view.insert.assert_called_with(ANY, 0, "message\n\n")

    def test_can_show_type_at_cursor(self):

        cmd = ShowHsTypeAtCursorCommand()
        (window, view) = default_mock_window()
        cmd.view = view
        setup_fake_backend(window)

        cmd.run(None)
        cmd.view.show_popup.assert_called_with(type_info)

    def test_can_copy_type_at_cursor(self):

        cmd = CopyHsTypeAtCursorCommand()
        (window, view) = default_mock_window()
        cmd.view = view
        setup_fake_backend(window)

        cmd.run(None)

        self.assertEqual(sublime.clipboard, type_info)

    def test_can_request_show_info_at_cursor(self):

        cmd = ShowHsInfoAtCursorCommand()
        (window, view) = default_mock_window()
        cmd.view = view

        setup_fake_backend(window, {'RequestGetSpanInfo': someFunc_span_info})

        cmd.run(None)
        cmd.view.show_popup.assert_called_with("someFunc :: IO ()  (Defined in src/Lib.hs:9:1)")

    def test_show_info_from_module(self):

        cmd = ShowHsInfoAtCursorCommand()
        (window, view) = default_mock_window()
        cmd.view = view


        setup_fake_backend(window, {'RequestGetSpanInfo':putStrLn_span_info})

        cmd.run(None)

        cmd.view.show_popup.assert_called_with("putStrLn :: String -> IO ()  (Imported from Prelude)")

    def test_goto_definition_at_cursor(self):

        cmd = GotoDefinitionAtCursorCommand()
        (window, view) = default_mock_window()
        cmd.view = view

        setup_fake_backend(window, {'RequestGetSpanInfo': someFunc_span_info})

        cmd.run(None)

        window.open_file.assert_called_with(cur_dir + "/projects/helloworld/src/Lib.hs:9:1", sublime.ENCODED_POSITION)

    def test_goto_definition_of_module(self):

        cmd = GotoDefinitionAtCursorCommand()
        (window, view) = default_mock_window()
        cmd.view = view

        cmd._handle_response(putStrLn_span_info.get('contents'))

        self.assertEqual("Cannot navigate to putStrLn, it is imported from Prelude", sublime.current_status)
