import unittest
from unittest.mock import MagicMock, Mock, ANY
from win import Win
from .stubs import sublime
from .mocks import cur_dir, default_mock_window
from utility import relative_view_file_name

def create_source_error(filePath, kind, message):
    return {
        "errorKind": kind,
        "errorMsg": message,
        "errorSpan": {
            "tag": "ProperSpan",
            "contents": {
                "spanFilePath": filePath,
                "spanFromLine": 1,
                "spanFromColumn": 1,
                "spanToLine": 1,
                "spanToColumn": 5
            }
        }
    }


class WinTests(unittest.TestCase):

    def test_highlight_type_clear(self):
        (window, view) = default_mock_window()

        Win(window).highlight_type([])

        view.set_status.assert_called_with("type_at_cursor", "")
        view.add_regions.assert_called_with("type_at_cursor", [], "storage.type", "", sublime.DRAW_OUTLINED)

    def test_highlight_no_errors(self):

        (window, view) = default_mock_window()

        panel = MagicMock()
        window.create_output_panel = Mock(return_value=panel)

        errors = []
        Win(window).handle_source_errors(errors)

        # panel recreated
        window.create_output_panel.assert_called_with("hide_errors")
        window.run_command.assert_any_call("hide_panel",  {"panel": "output.hide_errors"})
        panel.run_command.assert_called_with("clear_error_panel")
        panel.set_read_only.assert_any_call(False)

        # regions created in view
        view.add_regions.assert_any_call("errors", [], "invalid", "dot", sublime.DRAW_OUTLINED)
        view.add_regions.assert_any_call("warnings", [], "comment", "dot", sublime.DRAW_OUTLINED)

        # panel hidden and locked
        window.run_command.assert_called_with("hide_panel", {"panel": "output.hide_errors"})
        panel.set_read_only.assert_any_call(True)



    def test_highlight_errors_and_warnings(self):

        (window, view) = default_mock_window()

        panel = MagicMock()
        window.create_output_panel = Mock(return_value=panel)

        filePath = relative_view_file_name(view)
        error = create_source_error(filePath, "KindError", "<error message here>")
        warning = create_source_error(filePath, "KindWarning", "<warning message here>")
        errors = [error, warning]

        Win(window).handle_source_errors(errors)

        # panel recreated
        window.create_output_panel.assert_called_with("hide_errors")
        window.run_command.assert_any_call("hide_panel",  {"panel": "output.hide_errors"})
        # panel.run_command.assert_any_call("clear_error_panel")
        panel.set_read_only.assert_any_call(False)

        # panel should have received two messages
        panel.run_command.assert_any_call("append_to_error_panel", {"message": "src/Main.hs:1:1: KindError:\n<error message here>"})
        panel.run_command.assert_any_call("append_to_error_panel", {"message": "src/Main.hs:1:1: KindWarning:\n<warning message here>"})

        # regions added
        view.add_regions.assert_called_with("warnings", [ANY], "comment", "dot", sublime.DRAW_OUTLINED)
        view.add_regions.assert_any_call('errors', [ANY], 'invalid', 'dot', 2)

        # panel shown and locked
        window.run_command.assert_called_with("show_panel", {"panel": "output.hide_errors"})
        panel.set_read_only.assert_any_call(True)

    def test_opens_views_for_errors(self):

        (window, view) = default_mock_window()
        window.find_open_file = Mock(side_effect=[None, view]) # first call None, second call is created

        panel = MagicMock()
        window.create_output_panel = Mock(return_value=panel)

        error = create_source_error("src/Lib.hs", "KindError", "<error message here>")
        errors = [error]

        Win(window).handle_source_errors(errors)

        # should have opened the file for us.
        window.open_file.assert_called_with(cur_dir + "/projects/helloworld/src/Lib.hs")

        # panel recreated
        window.create_output_panel.assert_called_with("hide_errors")
        window.run_command.assert_any_call("hide_panel",  {"panel": "output.hide_errors"})
        # panel.run_command.assert_any_call("clear_error_panel")
        panel.set_read_only.assert_any_call(False)

        # panel should have received two messages
        panel.run_command.assert_any_call("append_to_error_panel", {"message": "src/Lib.hs:1:1: KindError:\n<error message here>"})

        # regions added
        view.add_regions.assert_called_with("warnings", [], "comment", "dot", sublime.DRAW_OUTLINED)
        view.add_regions.assert_any_call('errors', [ANY], 'invalid', 'dot', 2)

        # panel shown and locked
        window.run_command.assert_called_with("show_panel", {"panel": "output.hide_errors"})
        panel.set_read_only.assert_any_call(True)
