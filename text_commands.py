import sublime, sublime_plugin

from SublimeStackIDE.utility import *
from SublimeStackIDE.req import *
from SublimeStackIDE.stack_ide import *
from SublimeStackIDE.stack_ide_manager import *

class ClearErrorPanelCommand(sublime_plugin.TextCommand):
    """
    A clear_error_panel command to clear the error panel.
    """
    def run(self, edit):
        self.view.erase(edit, sublime.Region(0, self.view.size()))

class UpdateErrorPanelCommand(sublime_plugin.TextCommand):
    """
    An update_error_panel command to append text to the error panel.
    """
    def run(self, edit, message):
        self.view.insert(edit, self.view.size(), message + "\n\n")

class ShowHsTypeAtCursorCommand(sublime_plugin.TextCommand):
    """
    A show_hs_type_at_cursor command that requests the type of the
    expression under the cursor and, if available, shows it as a pop-up.
    """
    def run(self,edit):
        request = Req.get_exp_types(span_from_view_selection(self.view))
        send_request(self.view,request, self._handle_response)

    def _handle_response(self,response):
        info = type_info_for_sel(self.view,response)
        if info:
            (type_str,type_span) = info
            self.view.show_popup(type_str)


class ShowHsInfoAtCursorCommand(sublime_plugin.TextCommand):
    """
    A show_hs_info_at_cursor command that requests the info of the
    expression under the cursor and, if available, shows it as a pop-up.
    """
    def run(self,edit):
        request = Req.get_exp_info(span_from_view_selection(self.view))
        send_request(self.view,request, self._handle_response)

    def _handle_response(self,response):

        if len(response) < 1:
           return

        contents = response[0][0]["contents"]
        info = parse_info_result(response[0][0]["contents"])

        if info.file:
            source = "(Defined in {}:{}:{})".format(info.file, info.line, info.col)
        elif info.module:
            source = "(Imported from {})".format(info.module)

        self.view.show_popup("{} :: {}  {}".format(info.name,
                                                    info.type,
                                                    source))


class GotoDefinitionAtCursorCommand(sublime_plugin.TextCommand):
    """
    A goto_definition_at_cursor command that requests the info of the
    expression under the cursor and, if available, navigates to its location
    """
    def run(self,edit):
        request = Req.get_exp_info(span_from_view_selection(self.view))
        send_request(self.view,request, self._handle_response)

    def _handle_response(self,response):

        if len(response) < 1:
           return

        info = parse_info_result(response[0][0]["contents"])
        window = self.view.window()
        if info.file:
            full_path = os.path.join(first_folder(window), info.file)
            window.open_file(
              '{}:{}:{}'.format(full_path, info.line or 0, info.col or 0), sublime.ENCODED_POSITION)
        elif info.module:
            sublime.status_message("Cannot navigate to {}, it is imported from {}".format(info.name, info.module))
        else:
            sublime.status_message("{} not found!", info.name)

def parse_info_result(contents):
    """
    Extracts reponse into a reusable expression info object
    """
    module_keypath = ["idScope", "idImportedFrom", "moduleName"]
    type_keypath   = ["idProp", "idType"]
    name_keypath   = ["idProp", "idName"]
    def_file_keypath   = ["idProp", "idDefSpan", "contents", "spanFilePath"]
    def_line_keypath      = ["idProp", "idDefSpan", "contents", "spanFromLine"]
    def_col_keypath       = ["idProp", "idDefSpan", "contents", "spanFromColumn"]

    return ExpressionInfo(get_keypath(contents, name_keypath),
                            get_keypath(contents, type_keypath),
                            get_keypath(contents, module_keypath),
                            get_keypath(contents, def_file_keypath),
                            get_keypath(contents, def_line_keypath),
                            get_keypath(contents, def_col_keypath))

class ExpressionInfo():

    def __init__(self, name, type, module, file, line, col):
        self.name = name
        self.type = type
        self.module = module
        self.file = file
        self.line = line
        self.col = col


class CopyHsTypeAtCursorCommand(sublime_plugin.TextCommand):
    """
    A copy_hs_type_at_cursor command that requests the type of the
    expression under the cursor and, if available, puts it in the clipboard.
    """
    def run(self,edit):
        request = Req.get_exp_types(span_from_view_selection(self.view))
        send_request(self.view,request, self._handle_response)

    def _handle_response(self,response):
        info = type_info_for_sel(self.view,response)
        if info:
            (type_str,type_span) = info
            sublime.set_clipboard(type_str)
