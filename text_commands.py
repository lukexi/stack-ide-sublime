try:
    import sublime, sublime_plugin
except ImportError:
    from test.stubs import sublime, sublime_plugin

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from utility import span_from_view_selection, first_folder
from req import Req
from stack_ide_manager import send_request
from response import parse_span_info_response, parse_exp_types

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
        send_request(self.view.window(),request, self._handle_response)

    def _handle_response(self,response):
        types = list(parse_exp_types(response))
        if types:
            (type, span) = types[0] # types are ordered by relevance?
            self.view.show_popup(type)


class ShowHsInfoAtCursorCommand(sublime_plugin.TextCommand):
    """
    A show_hs_info_at_cursor command that requests the info of the
    expression under the cursor and, if available, shows it as a pop-up.
    """
    def run(self,edit):
        request = Req.get_exp_info(span_from_view_selection(self.view))
        send_request(self.view.window(), request, self._handle_response)

    def _handle_response(self,response):

        if len(response) < 1:
           return

        infos = parse_span_info_response(response)
        (props, scope), span = next(infos)

        if not props.defSpan is None:
            source = "(Defined in {}:{}:{})".format(props.defSpan.filePath, props.defSpan.fromLine, props.defSpan.fromColumn)
        elif scope.importedFrom:
            source = "(Imported from {})".format(scope.importedFrom.module)

        self.view.show_popup("{} :: {}  {}".format(props.name,
                                                    props.type,
                                                    source))


class GotoDefinitionAtCursorCommand(sublime_plugin.TextCommand):
    """
    A goto_definition_at_cursor command that requests the info of the
    expression under the cursor and, if available, navigates to its location
    """
    def run(self,edit):
        request = Req.get_exp_info(span_from_view_selection(self.view))
        send_request(self.view.window(),request, self._handle_response)

    def _handle_response(self,response):

        if len(response) < 1:
            return

        infos = parse_span_info_response(response)
        (props, scope), span = next(infos)
        window = self.view.window()
        if props.defSpan:
            full_path = os.path.join(first_folder(window), props.defSpan.filePath)
            window.open_file(
            '{}:{}:{}'.format(full_path, props.defSpan.fromLine or 0, props.defSpan.fromColumn or 0), sublime.ENCODED_POSITION)
        elif scope.importedFrom:
            sublime.status_message("Cannot navigate to {}, it is imported from {}".format(props.name, scope.importedFrom.module))
        else:
            sublime.status_message("{} not found!", props.name)

class CopyHsTypeAtCursorCommand(sublime_plugin.TextCommand):
    """
    A copy_hs_type_at_cursor command that requests the type of the
    expression under the cursor and, if available, puts it in the clipboard.
    """
    def run(self,edit):
        request = Req.get_exp_types(span_from_view_selection(self.view))
        send_request(self.view.window(), request, self._handle_response)

    def _handle_response(self,response):
        types = list(parse_exp_types(response))
        if types:
            (type, span) = types[0] # types are ordered by relevance?
            sublime.set_clipboard(type)
