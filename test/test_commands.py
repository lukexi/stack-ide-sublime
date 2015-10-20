import unittest
from unittest.mock import MagicMock, Mock, ANY

# import text_commands

# class CommandTests(unittest.TestCase):

#     def test_can_clear_panel(self):
#         cmd = text_commands.ClearErrorPanelCommand()
#         cmd.view = MagicMock()
#         cmd.run(None)
#         cmd.view.erase.assert_called_with(ANY, ANY)

#     def test_can_update_panel(self):
#         cmd = text_commands.UpdateErrorPanelCommand()
#         cmd.view = MagicMock()
#         cmd.view.size = Mock(return_value=0)
#         cmd.run(None, 'message')
#         cmd.view.insert.assert_called_with(ANY, 0, "message\n\n")

    # def test_can_show_type_at_cursor(self):
    #     cmd = stackide.ShowHsTypeAtCursorCommand()
    #     cmd.view = mock_view()
    #     cmd.view.show_popup = Mock()
    #     type_info = "YOLO -> Ded"
    #     span = {
    #         # "spanFilePath": relative_view_file_name(view),
    #         "spanFromLine": 1,
    #         "spanFromColumn": 1,
    #         "spanToLine": 1,
    #         "spanToColumn": 5
    #     }

    #     response = {"tag": "", "contents": [[type_info, span]]}
    #     backend = FakeBackend(response)
    #     instance = stackide.StackIDE(cmd.view.window(), backend)
    #     backend.handler = instance.handle_response
    #     stackide.supervisor = stackide.Supervisor(monitor=False)
    #     stackide.supervisor.window_instances[
    #         cmd.view.window().id()] = instance

    #     cmd.run(None)
    #     cmd.view.show_popup.assert_called_with(type_info)
    #     stackide.supervisor = None

    # def test_can_copy_type_at_cursor(self):
    #     cmd = stackide.CopyHsTypeAtCursorCommand()
    #     cmd.view = mock_view()
    #     cmd.view.show_popup = Mock()
    #     type_info = "YOLO -> Ded"
    #     span = {
    #         # "spanFilePath": relative_view_file_name(view),
    #         "spanFromLine": 1,
    #         "spanFromColumn": 1,
    #         "spanToLine": 1,
    #         "spanToColumn": 5
    #     }

    #     response = {"tag": "", "contents": [[type_info, span]]}
    #     backend = FakeBackend(response)
    #     instance = stackide.StackIDE(cmd.view.window(), backend)
    #     backend.handler = instance.handle_response

    #     stackide.supervisor = stackide.Supervisor(monitor=False)
    #     stackide.supervisor.window_instances[
    #         cmd.view.window().id()] = instance

    #     cmd.run(None)
    #     self.assertEqual(sublime.clipboard, type_info)
    #     stackide.supervisor = None

    # def test_can_request_show_info_at_cursor(self):
    #     cmd = stackide.ShowHsInfoAtCursorCommand()
    #     cmd.view = mock_view()
    #     cmd.view.show_popup = Mock()

    #     # response = {"tag": "", "contents": [[{"contents" : someFunc_span_info}, {}]]}
    #     backend = FakeBackend(someFunc_span_info)
    #     instance = stackide.StackIDE(cmd.view.window(), backend)
    #     backend.handler = instance.handle_response

    #     stackide.supervisor = stackide.Supervisor(monitor=False)
    #     stackide.supervisor.window_instances[
    #         cmd.view.window().id()] = instance

    #     cmd.run(None)
    #     cmd.view.show_popup.assert_called_with("someFunc :: IO ()  (Defined in src/Lib.hs:9:1)")
    #     stackide.supervisor = None

    # def test_show_info_from_module(self):
    #     cmd = stackide.ShowHsInfoAtCursorCommand()
    #     cmd.view = mock_view()
    #     cmd.view.show_popup = Mock()
    #     # response = {"tag": "", "contents": [[{"contents" : putStrLn_span_info}, {}]]}
    #     backend = FakeBackend(putStrLn_span_info)
    #     instance = stackide.StackIDE(cmd.view.window(), backend)
    #     backend.handler = instance.handle_response

    #     stackide.supervisor = stackide.Supervisor(monitor=False)
    #     stackide.supervisor.window_instances[
    #         cmd.view.window().id()] = instance

    #     cmd.run(None)
    #     cmd.view.show_popup.assert_called_with("putStrLn :: String -> IO ()  (Imported from Prelude)")
    #     stackide.supervisor = None

    # def test_goto_definition_at_cursor(self):
    #     global cur_dir
    #     cmd = stackide.GotoDefinitionAtCursorCommand()
    #     cmd.view = mock_view()
    #     cmd.view.show_popup = Mock()
    #     backend = FakeBackend(someFunc_span_info)
    #     window = cmd.view.window()
    #     window.open_file = Mock()
    #     instance = stackide.StackIDE(window, backend)
    #     backend.handler = instance.handle_response

    #     stackide.supervisor = stackide.Supervisor(monitor=False)
    #     stackide.supervisor.window_instances[
    #         cmd.view.window().id()] = instance

    #     cmd.run(None)
    #     window.open_file.assert_called_with(cur_dir + "/mocks/helloworld/src/Lib.hs:9:1", sublime.ENCODED_POSITION)
    #     stackide.supervisor = None

    # def test_goto_definition_of_module(self):
    #     global cur_dir
    #     cmd = stackide.GotoDefinitionAtCursorCommand()
    #     cmd.view = mock_view()
    #     cmd.view.show_popup = Mock()
    #     window = cmd.view.window()
    #     window.status_message = Mock()
    #     cmd._handle_response(putStrLn_span_info.get('contents'))
    #     self.assertEqual("Cannot navigate to putStrLn, it is imported from Prelude", sublime.current_status)

if __name__ == '__main__':
    unittest.main()
