from itertools import groupby
import os

try:
    import sublime
except ImportError:
    from test.stubs import sublime
from utility import first_folder, view_region_from_span, filter_enclosing, shorten_module_prefix
from response import parse_source_errors, parse_exp_types

class Win:
    """
    Operations on Sublime windows that are relevant to us
    """

    show_popup = False

    def __init__(self,window):
        self.window = window

    def update_completions(self, completions):
        """
        Dispatches to the dummy UpdateCompletionsCommand, which is intercepted
        by StackIDEAutocompleteHandler's on_window_command to update its list
        of completions.
        """
        self.window.run_command("update_completions", {"completions":completions})

    def find_view_for_path(self, relative_path):
        full_path = os.path.join(first_folder(self.window), relative_path)
        return self.window.find_open_file(full_path)

    def open_view_for_path(self, relative_path):
        full_path = os.path.join(first_folder(self.window), relative_path)
        self.window.open_file(full_path)

    def highlight_type(self, exp_types):
        """
        ide-backend gives us a wealth of type info for the cursor. We only use the first,
        most specific one for now, but it gives us the types all the way out to the topmost
        expression.
        """
        type_spans = list(parse_exp_types(exp_types))
        if type_spans:
            view = self.window.active_view()
            type_span = next(filter_enclosing(view, view.sel()[0], type_spans), None)
            if type_span is not None:
                (_type, span) = type_span
                view.set_status("type_at_cursor", _type)
                view.add_regions("type_at_cursor", [view_region_from_span(view, span)], "storage.type", "", sublime.DRAW_OUTLINED)
                if Win.show_popup:
                    view.show_popup(shorten_module_prefix(_type))
                return

        # Clear type-at-cursor display     
        for view in self.window.views():       
            view.set_status("type_at_cursor", "")      
            view.add_regions("type_at_cursor", [], "storage.type", "", sublime.DRAW_OUTLINED)


    def handle_source_errors(self, source_errors):
        """
        Makes sure views containing errors are open and shows error messages + highlighting
        """

        errors = list(parse_source_errors(source_errors))

        # TODO: we should pass the errorKind too if the error has no span
        error_panel = self.reset_error_panel()
        for error in errors:
            error_panel.run_command("update_error_panel", {"message": repr(error)})

        if errors:
            self.window.run_command("show_panel", {"panel":"output.hide_errors"})
        else:
            self.window.run_command("hide_panel", {"panel":"output.hide_errors"})

        error_panel.set_read_only(True)

        file_errors = list(filter(lambda error: error.span, errors))
        # First, make sure we have views open for each error
        need_load_wait = False
        paths = set(error.span.filePath for error in file_errors)
        for path in paths:
            view = self.find_view_for_path(path)
            if not view:
                need_load_wait = True
                self.open_view_for_path(path)

        # If any error-holding files need to be opened, wait briefly to
        # make sure the file is loaded before trying to annotate it
        if need_load_wait:
            sublime.set_timeout(lambda: self.highlight_errors(file_errors), 100)
        else:
            self.highlight_errors(file_errors)


    def reset_error_panel(self):
        """
        Creates and configures the error panel for the current window
        """
        panel = self.window.create_output_panel("hide_errors")
        panel.set_read_only(False)

        # This turns on double-clickable error/warning messages in the error panel
        # using a regex that looks for the form file_name:line:column
        panel.settings().set("result_file_regex", "^(..[^:]*):([0-9]+):?([0-9]+)?:? (.*)$")

        # Seems to force the panel to refresh after we clear it:
        self.window.run_command("hide_panel", {"panel": "output.hide_errors"})

        # Clear the panel. TODO: should be unnecessary? https://www.sublimetext.com/forum/viewtopic.php?f=6&t=2044
        panel.run_command("clear_error_panel")

        # TODO store the panel somewhere so we can reuse it.
        return panel


    def highlight_errors(self, errors):
        """
        Highlights the relevant regions for each error in open views
        """

        # We gather each error by the file view it should annotate
        # so we can add regions in bulk to each view.
        error_regions_by_view_id = {}
        warning_regions_by_view_id = {}
        for path, errors_by_path in groupby(errors, lambda error: error.span.filePath):
            view = self.find_view_for_path(path)
            for kind, errors_by_kind in groupby(errors_by_path, lambda error: error.kind):
                if kind == 'KindWarning':
                    warning_regions_by_view_id[view.id()] = list(view_region_from_span(view, error.span) for error in errors_by_kind)
                else:
                    error_regions_by_view_id[view.id()] = list(view_region_from_span(view, error.span) for error in errors_by_kind)

        # Add error/warning regions to their respective views
        for view in self.window.views():
            view.add_regions("errors", error_regions_by_view_id.get(view.id(), []), "invalid", "dot", sublime.DRAW_OUTLINED)
            view.add_regions("warnings", warning_regions_by_view_id.get(view.id(), []), "comment", "dot", sublime.DRAW_OUTLINED)


