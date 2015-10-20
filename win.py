import sublime, sublime_plugin
from SublimeStackIDE.utility import *
from SublimeStackIDE.span import *

class Win:
    """
    Operations on Sublime windows that are relevant to us
    """

    def __init__(self,view_or_window):
        self.window = get_window(view_or_window)


    def update_completions(self, completions):
        """
        Dispatches to the dummy UpdateCompletionsCommand, which is intercepted
        by StackIDEAutocompleteHandler's on_window_command to update its list
        of completions.
        """
        self.window.run_command("update_completions", {"completions":completions})


    def highlight_type(self, types):
        """
        ide-backend gives us a wealth of type info for the cursor. We only use the first,
        most specific one for now, but it gives us the types all the way out to the topmost
        expression.
        """
        if types:
            # Display the first type in a region and in the status bar
            view = self.window.active_view()
            (type_string,type_span) = type_info_for_sel(view,types)
            span = Span.from_json(type_span, self.window)
            if span:
                if Settings.show_popup():
                    view.show_popup(type_string)
                view.set_status("type_at_cursor", type_string)
                view.add_regions("type_at_cursor", [span.in_view.region], "storage.type", "", sublime.DRAW_OUTLINED)
        else:
            # Clear type-at-cursor display
            for view in self.window.views():
                view.set_status("type_at_cursor", "")
                view.add_regions("type_at_cursor", [], "storage.type", "", sublime.DRAW_OUTLINED)


    def highlight_errors(self, errors):
        """
        Places errors in the error panel, and highlights the relevant regions for each error.
        """
        # First, make sure we have views open for each error
        need_load_wait = False
        for error in errors:
            span = None
            proper_span = error.get("errorSpan")
            if proper_span.get("tag") == "ProperSpan":
                contents = proper_span.get("contents")
                full_path = Span.get_full_path(contents, self.window)
                if not self.window.find_open_file(full_path):
                    need_load_wait = True
                self.window.open_file(full_path)

        # If any error-holding files need to be opened, wait briefly to 
        # make sure the file is loaded before trying to annotate it
        if need_load_wait:
            sublime.set_timeout(lambda: self.highlight_errors_really(errors), 100)
        else:
            self.highlight_errors_really(errors)

    def highlight_errors_really(self, errors):
        """
        Places errors in the error panel, and highlights the relevant regions for each error.
        """
        error_panel = self.window.create_output_panel("hide_errors")
        error_panel.set_read_only(False)

        # This turns on double-clickable error/warning messages in the error panel
        # using a regex that looks for the form file_name:line:column
        error_panel.settings().set("result_file_regex", "^(..[^:]*):([0-9]+):?([0-9]+)?:? (.*)$")

        # Seems to force the panel to refresh after we clear it:
        self.window.run_command("hide_panel", {"panel":"output.hide_errors"})
        # Clear the panel
        error_panel.run_command("clear_error_panel")

        # We gather each error by the file view it should annotate
        # so we can add regions in bulk to each view.
        errors_by_view_id = {}
        warnings_by_view_id = {}
        for error in errors:
            # Stack-ide can return different kinds of Spans for errors; we only support ProperSpans currently
            span = None
            proper_span = error.get("errorSpan")
            if proper_span.get("tag") == "ProperSpan":
                contents = proper_span.get("contents")
                # Construct the span from the JSON
                span = Span.from_json(contents, self.window)

            # Text commands only accept Value types, so we perform the conversion of the error span to a string here
            # to pass to update_error_panel.
            # TODO we should pass the errorKind too if the error has no span
            message = span.as_error_message(error) if span else error.get("errorMsg")

            # Add the error to the error panel
            error_panel.run_command("update_error_panel", {"message":message})

            # Collect error and warning spans by view for annotations
            span_view = span.in_view if span else None
            if span_view:
                # Log.debug("Adding error at "+ str(span) + ": " + str(error.get("errorMsg")))
                kind = error.get("errorKind")
                if kind == "KindWarning":
                    warning_regions_for_view = warnings_by_view_id.get(span_view.view.id(), [])
                    warning_regions_for_view += [span_view.region]
                    warnings_by_view_id[span_view.view.id()] = warning_regions_for_view
                else:
                    error_regions_for_view = errors_by_view_id.get(span_view.view.id(), [])
                    error_regions_for_view += [span_view.region]
                    errors_by_view_id[span_view.view.id()] = error_regions_for_view

            else:
                Log.warning("Unhandled error tag type: ", proper_span)

        # Add error/warning regions to their respective views
        for view in self.window.views():
            # Return an empty list if there are no errors for the view, so that we clear the error regions
            error_regions = errors_by_view_id.get(view.id(), [])
            view.add_regions("errors", error_regions, "invalid", "dot", sublime.DRAW_OUTLINED)
            warning_regions = warnings_by_view_id.get(view.id(), [])
            view.add_regions("warnings", warning_regions, "comment", "dot", sublime.DRAW_OUTLINED)

        if errors:
            # Show the panel
            self.window.run_command("show_panel", {"panel":"output.hide_errors"})
        else:
            # Hide the panel
            self.window.run_command("hide_panel", {"panel":"output.hide_errors"})

        error_panel.set_read_only(True)







