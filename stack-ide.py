import sublime, sublime_plugin
import subprocess, os
import sys
import threading
import time
import json

#############################
# Plugin development utils
#############################
# Ensure existing processes are killed when we 
# save the plugin to prevent proliferation of 
# stack-ide session.13953 folders
stack_ide_processes = []

def plugin_loaded():
    print("stack-ide-sublime loaded.")
    
def plugin_unloaded():
    global stack_ide_processes
    kill_all_processes()

def kill_all_processes():
    global stack_ide_processes
    print("Killing all stack-ide-sublime instances: " + str(stack_ide_processes))
    for process in stack_ide_processes:
        process.end()
    stack_ide_processes = []

def register_process(process):
    global stack_ide_processes
    if not stack_ide_processes:
        stack_ide_processes = []
    stack_ide_processes += [process]
    print(stack_ide_processes)


#############################
# Utility functions
#############################

def first_folder(window):
    """
    We only support running one stack-ide instance per window currently,
    on the first folder open in that window.
    """
    return window.folders()[0]

def relative_view_file_name(view):
    """
    ide-backend expects file names as relative to the cabal project root
    """
    return view.file_name().replace(first_folder(view.window()) + "/", "")

def send_request(view, request):
    """
    Call the view's window's SendIdeBackendRequestCommand instance with the given request.
    """
    view.window().run_command("send_ide_backend_request", {"request":request})

def span_from_view_selection(view):
    return span_from_view_region(view, view.sel()[0])

def span_from_view_region(view, region):
    (from_line, from_col) = view.rowcol(region.begin())
    (to_line,   to_col)   = view.rowcol(region.end())
    return {
        "spanFilePath": relative_view_file_name(view),
        "spanFromLine": from_line + 1,
        "spanFromColumn": to_col + 1,
        "spanToLine": to_line + 1,
        "spanToColumn": to_col + 1
        }

def view_region_from_json_span(span, window):
    if span == None:
        return None
    file_path    = span.get("spanFilePath")
    if file_path == None:
        return None
    from_line    = span.get("spanFromLine")
    from_column  = span.get("spanFromColumn")
    to_line      = span.get("spanToLine")
    to_column    = span.get("spanToColumn")
    full_path    = first_folder(window) + "/" + file_path
    view         = window.find_open_file(full_path)
    if view:
        from_point = view.text_point(from_line - 1, from_column - 1)
        to_point   = view.text_point(to_line   - 1, to_column   - 1)
        region     = sublime.Region(from_point, to_point)
        return (view, region)

def module_name_for_view(view):
    module_name = view.substr(view.find("^module [A-Za-z._]*", 0)).replace("module ", "")
    return module_name


#############################
# Text commands
#############################

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
    def run(self, edit, errors):
        self.view.insert(edit, self.view.size(), str(errors) + "\n\n")

#############################
# Event Listeners
#############################

class IdeBackendSaveListener(sublime_plugin.EventListener):
    """
    Ask stack-ide to recompile the saved source file, 
    then request a report of source errors.
    """
    def on_post_save(self, view):
        request = {
            "tag":"RequestUpdateSession",
            "contents": []
            }
        send_request(view, request)
        send_request(view, { "tag": "RequestGetSourceErrors", "contents":[] })

class IdeBackendTypeAtCursorHandler(sublime_plugin.EventListener):
    """
    Ask stack-ide for the type at the cursor each 
    time it changes position.
    """
    def on_selection_modified(self, view):
        # Only try to get types for views into files
        # (rather than e.g. the find field or the console pane)
        if view.file_name():
            # Uncomment to see the scope at the cursor:
            # print(view.scope_name(view.sel()[0].begin()))
            request = { 
                "tag": "RequestGetExpTypes", 
                "contents" :  span_from_view_selection(view)
                }
            send_request(view, request)

class IdeBackendAutocompleteHandler(sublime_plugin.EventListener):
    """
    Dispatches autocompletion requests to stack-ide.
    """
    def __init__(self):
        super(IdeBackendAutocompleteHandler, self).__init__()
        self.returned_completions = []

    def on_query_completions(self, view, prefix, locations):
        # Check if this completion query is due to our refreshing the completions list
        # after receiving a response from stack-ide, and if so, don't send
        # another request for completions.
        if not view.settings().get("refreshing_auto_complete"):
            request = {
                "tag":"RequestGetAutocompletion", 
                "contents": {
                        "autocompletionFilePath": relative_view_file_name(view), 
                        "autocompletionPrefix": prefix
                    }
                }
            send_request(view, request)

        # Clear the flag to uninhibit future completion queries
        view.settings().set("refreshing_auto_complete", False)

        # Sublime Text 3 expects completions in the form of [(annotation, name)],
        # where annotation is <name>\t<hint1>\t<hint2>
        # where hint1/hint2/etc. are optional auxiliary information that will
        # be displayed in italics to the right of the name.
        def annotation_from_completion(completion):
            return "\t".join(
                filter(lambda x: x is not None, 
                    map(completion.get, 
                        ["autocompletionInfoName", "autocompletionType", "autocompletionInfoDefinedIn"])))

        annotations = map(annotation_from_completion, self.returned_completions)
        names       = map(lambda x: x.get("autocompletionInfoName"),    self.returned_completions)

        annotated_completions = list(zip(annotations, names))
        print("Returning: ", annotated_completions)
        return annotated_completions


    def on_window_command(self, window, command_name, args):
        """
        Implements a hacky way of returning data to the IdeBackendAutocompleteHandler instance,
        wherein SendIdeBackendRequestCommand calls a update_completions command on the window,
        which is really just a dummy command that we intercept here in order to assign the resulting
        completions to returned_completions to then, finally, return the next time on_query_completions
        is called.
        """
        if args == None:
            return None
        completions = args.get("completions")
        if command_name == "update_completions" and completions:
            # print("INTERCEPTED:\n " + str(completions) + "\n")
            
            self.returned_completions = completions

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


#############################
# Window commands
#############################

class UpdateCompletionsCommand(sublime_plugin.WindowCommand):
    """
    This class only exists so that the command can be called and intercepted by
    IdeBackendAutocompleteHandler to update its completions list.
    """
    def run(self, completions):
        return None

class SendIdeBackendRequestCommand(sublime_plugin.WindowCommand):
    """
    Runs a per-window process of stack-ide.
    (Sublime Text uses the class name to determine the name of the command
    the class executes when called, i.e. send_ide_backend_request)
    """

    def __init__(self, window):
        super(SendIdeBackendRequestCommand, self).__init__(window)
        register_process(self)

        self.boot_ide_backend()
        
        self.run({ "tag": "RequestGetSourceErrors", "contents":[] })

    def boot_ide_backend(self):
        """
        Start up a stack-ide subprocess for the window, and a thread to consume its stdout.
        """
        print("Launching HIDE in ", first_folder(self.window)) 
        
        # Assumes the library target name is the same as the project dir
        (project_in, project_name) = os.path.split(first_folder(self.window))
        self.process = subprocess.Popen(["stack", "ide", project_name],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=first_folder(self.window)
            )

        self.stdoutThread = threading.Thread(target=self.read_stdout)
        self.stdoutThread.start()
        
        self.stderrThread = threading.Thread(target=self.read_stderr)
        self.stderrThread.start()

    def end(self):
        """
        Ask stack-ide to shut down.
        """
        self.run({"tag":"RequestShutdownSession", "contents":[]})

    def run(self, request):
        """
        Pass a request to stack-ide.
        Called via run_command("send_ide_backend_request", {"request":})
        """
        if self.process:
            print("Sending request: ", request)
            encodedString = json.JSONEncoder().encode(request) + "\n"
            self.process.stdin.write(bytes(encodedString, 'UTF-8'))
            self.process.stdin.flush()

    def read_stderr(self):
        """
        Reads any errors from the stack-ide process.
        """
        while self.process.poll() is None:
            try:
                print("Stack-IDE error: ", self.process.stderr.readline().decode('UTF-8'))
            except:
                print("Stack-IDE stderr process ending due to exception: ", sys.exc_info())
                return;
        print("Stack-IDE stderr process ended.")

    def read_stdout(self):
        """
        Reads JSON responses from stack-ide and dispatch them to
        various main thread handlers.
        """
        while self.process.poll() is None:
            try:
                raw = self.process.stdout.readline().decode('UTF-8')
                if not raw:
                    return
                # print("Raw response: ", raw)

                data = json.loads(raw)
                print(data)
                
                response = data.get("tag")
                contents = data.get("contents")

                # Pass progress messages to the status bar
                if response == "ResponseUpdateSession":
                    if contents != None:
                        progressMessage = contents.get("progressParsedMsg")
                        if progressMessage:
                            sublime.status_message(progressMessage)
                # Pass autocompletion responses to the completions handler
                # (via our window command hack - see note in on_window_command)
                elif response == "ResponseGetAutocompletion":
                    if contents != None:
                        sublime.set_timeout(lambda: self.update_completions(contents), 0)
                # Pass source error responses to the error highlighter
                elif response == "ResponseGetSourceErrors":
                    if contents != None:
                        sublime.set_timeout(lambda: self.highlight_errors(contents), 0)
                # Pass type information to the type highlighter
                elif response == "ResponseGetExpTypes":
                    if contents != None:
                        sublime.set_timeout(lambda: self.highlight_type(contents), 0)
                else:
                    print("Unhandled response: ", data)
                
            except:
                print("Stack-IDE stdout process ending due to exception: ", sys.exc_info())
                self.process.terminate()
                self.process = None
                return;
        print("Stack-IDE stdout process ended.")

    def update_completions(self, completions):
        """
        Dispatches to the dummy UpdateCompletionsCommand, which is intercepted
        by IdeBackendAutocompleteHandler's on_window_command to update its list
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
            first_type = types[0]
            [type_string, span] = types[0]
            view_and_region = view_region_from_json_span(span, self.window)
            if view_and_region:
                (view, region) = view_and_region
                view.set_status("type_at_cursor", type_string)
                view.add_regions("type_at_cursor", [region], "storage.type", "", sublime.DRAW_OUTLINED)
        else:
            # Clear type-at-cursor display
            for view in self.window.views():
                view.set_status("type_at_cursor", "")
                view.add_regions("type_at_cursor", [], "invalid", "", sublime.DRAW_OUTLINED)


    def highlight_errors(self, errors):
        """
        Places errors in the error panel, and highlights the relevant regions for each error.
        """
        error_panel = self.window.create_output_panel("hide_errors")
        error_panel.set_read_only(False)
        
        # Seems to force the panel to refresh after we clear it:
        self.window.run_command("hide_panel", {"panel":"output.hide_errors"})
        # Clear the panel
        error_panel.run_command("clear_error_panel")

        # Gather each error by the file view it should annotate
        errors_by_view_id = {}
        for error in errors:
            msg = error.get("errorMsg")
            error_panel.run_command("update_error_panel", {"errors":msg})
            proper_span = error.get("errorSpan")
            if proper_span.get("tag") == "ProperSpan":
                span = proper_span.get("contents")
                if span:
                    # kind = error.get("errorKind")
                    view_and_region = view_region_from_json_span(span, self.window)
                    print("View and region: ", view_and_region)

                    if view_and_region:
                        (view_for_error, region) = view_and_region

                        print("Adding error at "+ str(span) + ": " + str(msg))

                        error_regions_for_view = errors_by_view_id.get(view_for_error.id(), [])
                        error_regions_for_view += [region]
                        errors_by_view_id[view_for_error.id()] = error_regions_for_view
            else:
                print("Unhandled error tag type: ", proper_span)

        # Add error regions to their respective views
        for view in self.window.views():
            # Return an empty list if there are no errors for the view, so that we clear the error regions
            error_regions = errors_by_view_id.get(view.id(), [])
            view.add_regions("errors", error_regions, "invalid", "dot", sublime.DRAW_OUTLINED)
                
        if errors:
            # Show the panel
            self.window.run_command("show_panel", {"panel":"output.hide_errors"})
        else:
            # Hide the panel
            self.window.run_command("hide_panel", {"panel":"output.hide_errors"})


        error_panel.set_read_only(True)

    def __del__(self):
        if self.process:
            self.process.terminate()
            self.process = None


