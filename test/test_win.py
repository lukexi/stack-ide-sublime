import unittest
from unittest.mock import MagicMock, Mock, ANY
from win import Win
from .stubs import sublime
from .mocks import mock_view, mock_window, cur_dir
from utility import relative_view_file_name

class WinTests(unittest.TestCase):

    def test_highlight_type_clear(self):
        window = mock_window([cur_dir + '/projects/helloworld'])
        view = mock_view('src/Main.hs', window)

        Win(window).highlight_type([])
        view.set_status.assert_called_with("type_at_cursor", "")
        view.add_regions.assert_called_with("type_at_cursor", [], "storage.type", "", sublime.DRAW_OUTLINED)

    def test_highlight_no_errors(self):
        window = mock_window([cur_dir + '/projects/helloworld'])
        view = mock_view('src/Main.hs', window)

        window.run_command = Mock()

        panel = MagicMock()

        window.create_output_panel = Mock(return_value=panel)
        errors = []
        Win(window).handle_source_errors(errors)
        window.create_output_panel.assert_called_with("hide_errors")

        panel.settings().set.assert_called_with("result_file_regex", "^(..[^:]*):([0-9]+):?([0-9]+)?:? (.*)$")
        window.run_command.assert_any_call("hide_panel",  {"panel": "output.hide_errors"})
        panel.run_command.assert_called_with("clear_error_panel")
        panel.set_read_only.assert_any_call(False)

        view.add_regions.assert_any_call("errors", [], "invalid", "dot", sublime.DRAW_OUTLINED)
        view.add_regions.assert_any_call("warnings", [], "comment", "dot", sublime.DRAW_OUTLINED)

        window.run_command.assert_called_with("hide_panel", {"panel": "output.hide_errors"})
        panel.set_read_only.assert_any_call(True)

    def test_highlight_errors_and_warnings(self):

        window = mock_window([cur_dir + '/projects/helloworld'])
        view = mock_view('src/Main.hs', window)

        window.run_command = Mock()
        panel = MagicMock()
        window.create_output_panel = Mock(return_value=panel)
        error = {
            "errorKind": "KindError",
            "errorMsg": "<error message here>",
            "errorSpan": {
                "tag": "ProperSpan",
                "contents": {
                    "spanFilePath": relative_view_file_name(view),
                    "spanFromLine": 1,
                    "spanFromColumn": 1,
                    "spanToLine": 1,
                    "spanToColumn": 5
                }
            }
        }
        warning = {
            "errorKind": "KindWarning",
            "errorMsg": "<warning message here>",
            "errorSpan": {
                "tag": "ProperSpan",
                "contents": {
                    "spanFilePath": relative_view_file_name(view),
                    "spanFromLine": 1,
                    "spanFromColumn": 1,
                    "spanToLine": 1,
                    "spanToColumn": 5
                }
            }
        }
        errors = [error, warning]
        Win(window).handle_source_errors(errors)
        window.create_output_panel.assert_called_with("hide_errors")

        panel.settings().set.assert_called_with("result_file_regex", "^(..[^:]*):([0-9]+):?([0-9]+)?:? (.*)$")
        window.run_command.assert_any_call("hide_panel",  {"panel": "output.hide_errors"})
        # panel.run_command.assert_any_call("clear_error_panel")
        panel.set_read_only.assert_any_call(False)

        # panel should have received messages
        panel.run_command.assert_any_call("update_error_panel", {"message": "src/Main.hs:1:1: KindError:\n<error message here>"})
        panel.run_command.assert_any_call("update_error_panel", {"message": "src/Main.hs:1:1: KindWarning:\n<warning message here>"})

        view.add_regions.assert_called_with("warnings", [ANY], "comment", "dot", sublime.DRAW_OUTLINED)
        view.add_regions.assert_any_call('errors', [ANY], 'invalid', 'dot', 2)
        window.run_command.assert_called_with("show_panel", {"panel": "output.hide_errors"})
        panel.set_read_only.assert_any_call(True)
