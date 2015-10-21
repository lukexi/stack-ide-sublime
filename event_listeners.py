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
import response as res


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

    def on_query_completions(self, view, prefix, locations):

        if not is_haskell_view(view):
            return

        window = view.window()
        if not StackIDEManager.is_running(window):
            return

        # Check if this completion query is due to our refreshing the completions list
        # after receiving a response from stack-ide, and if so, don't send
        # another request for completions.
        if not view.settings().get("refreshing_auto_complete"):
            request = Req.get_autocompletion(filepath=relative_view_file_name(view),prefix=prefix)
            send_request(window, request, Win(window).update_completions)

        # Clear the flag to uninhibit future completion queries
        view.settings().set("refreshing_auto_complete", False)
        return list(self.format_completion(*completion) for completion in self.returned_completions)


    def format_completion(self, prop, scope):
        return ["{}\t{}\t{}".format(prop.name,
                                    prop.type or '',
                                    scope.importedFrom.module if scope else ''),
                 prop.name]


    def on_window_command(self, window, command_name, args):
        """
        Implements a hacky way of returning data to the StackIDEAutocompleteHandler instance,
        wherein SendStackIDERequestCommand calls a update_completions command on the window,
        which is really just a dummy command that we intercept here in order to assign the resulting
        completions to returned_completions to then, finally, return the next time on_query_completions
        is called.
        """
        if not StackIDEManager.is_running(window):
            return
        if args == None:
            return None
        completions = args.get("completions")
        if command_name == "update_completions" and completions:
            # Log.debug("INTERCEPTED:\n " + str(completions) + "\n")
            self.returned_completions = list(res.parse_autocompletions(completions))

            # Hide the auto_complete popup so we can reopen it,
            # triggering a new on_query_completions
            # call to pickup our new self.returned_completions.
            window.active_view().run_command('hide_auto_complete')

            def reactivate():
                # We read this in on_query_completions to prevent sending a duplicate
                # request for completions when we're only trying to re-trigger the completions
                # popup; otherwise we get an infinite loop of
                #   autocomplete > request completions > receive response > close/reopen to refresh
                # > autocomplete > request completions > etc.
                window.active_view().settings().set("refreshing_auto_complete", True)
                window.active_view().run_command('auto_complete', {
                        'disable_auto_insert': True,
                        # 'api_completions_only': True,
                        'next_competion_if_showing': False
                    })
            # Wait one runloop before reactivating, to give the hide command a chance to finish
            sublime.set_timeout(reactivate, 0)
        return None

