try:
    import sublime_plugin, sublime
except ImportError:
    from test.stubs import sublime, sublime_plugin

import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from utility import is_haskell_view, relative_view_file_name, span_from_view_selection
from req import Req
from win import Win
from stack_ide_manager import StackIDEManager, send_request
from response import parse_autocompletions

class StackIDESaveListener(sublime_plugin.EventListener):
    """
    Ask stack-ide to recompile the saved source file,
    then request a report of source errors.
    """
    def on_post_save(self, view):

        if not is_haskell_view(view):
            return

        if not StackIDEManager.is_running(view.window()):
            return

        StackIDEManager.for_window(view.window()).update_files([relative_view_file_name(view)])

class StackIDETypeAtCursorHandler(sublime_plugin.EventListener):
    """
    Ask stack-ide for the type at the cursor each
    time it changes position.
    """
    def on_selection_modified(self, view):

        if not is_haskell_view(view):
            return

        window = view.window()
        if not StackIDEManager.is_running(window):
            return

        # Only try to get types for views into files
        # (rather than e.g. the find field or the console pane)
        if view.file_name():
            # Uncomment to see the scope at the cursor:
            # Log.debug(view.scope_name(view.sel()[0].begin()))
            request = Req.get_exp_types(span_from_view_selection(view))
            send_request(window, request, Win(window).highlight_type)


class StackIDEAutocompleteHandler(sublime_plugin.EventListener):
    """
    Dispatches autocompletion requests to stack-ide.
    """
    def __init__(self):
        super(StackIDEAutocompleteHandler, self).__init__()
        self.returned_completions = []
        self.view = None
        self.refreshing = False

    def on_query_completions(self, view, prefix, locations):

        if not is_haskell_view(view):
            return

        window = view.window()
        if not StackIDEManager.is_running(window):
            return
        # Check if this completion query is due to our refreshing the completions list
        # after receiving a response from stack-ide, and if so, don't send
        # another request for completions.
        if not self.refreshing:
            self.view = view
            request = Req.get_autocompletion(filepath=relative_view_file_name(view),prefix=prefix)
            send_request(window, request, self._handle_response)

        # Clear the flag to allow future completion queries
        self.refreshing = False
        return list(self.format_completion(*completion) for completion in self.returned_completions)


    def format_completion(self, prop, scope):
        return ["{}\t{}\t{}".format(prop.name,
                                    prop.type or '',
                                    scope.importedFrom.module if scope else ''),
                 prop.name]

    def _handle_response(self, response):
        self.returned_completions = list(parse_autocompletions(response))
        self.view.run_command('hide_auto_complete')
        sublime.set_timeout(self.run_auto_complete, 0)


    def run_auto_complete(self):
        self.refreshing = True
        self.view.run_command("auto_complete", {
            'disable_auto_insert': True,
            # 'api_completions_only': True,
            'next_completion_if_showing': False,
            # 'auto_complete_commit_on_tab': True,
        })
