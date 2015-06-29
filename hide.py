import sublime, sublime_plugin
import subprocess, os
import sys
import threading
import time
import json

def first_folder(window):
    """
    We only support running one ide-backend-client instance per window currently,
    on the first folder open in that window.
    """
    return window.folders()[0]

def relative_view_file_name(view):
    """
    ide-backend expects file names as relative to the cabal project root
    """
    return view.file_name().replace(first_folder(view.window()) + "/", "")


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

class IdeBackendSaveListener(sublime_plugin.EventListener):
    """
    Ask ide-backend-client to recompile the saved source file, 
    then request a report of source errors.
    """
    def on_post_save(self, view):
        request = {
            "request":"updateSession",
            "update": [
                { "update": "updateSourceFileFromFile"
                , "filePath": relative_view_file_name(view)
                }
            ]
            }
        send_request(view, request)
        send_request(view, { "request": "getSourceErrors" })

def send_request(view, request):
    """
    Call the view's window's SendIdeBackendRequestCommand instance with the given request.
    """
    view.window().run_command("send_ide_backend_request", {"request":request})

class IdeBackendAutocompleteHandler(sublime_plugin.EventListener):

    def __init__(self):
        super(IdeBackendAutocompleteHandler, self).__init__()
        self.returned_completions = []

    def on_query_completions(self, view, prefix, locations):
        request = {
            "request":"getAutocompletion", 
            "autocomplete": {
                "filePath": relative_view_file_name(view), 
                "prefix": prefix
                } 
            }
        send_request(view, request)

        # Sublime Text 3 expects completions in the form of [(annotation, name)],
        # where annotation is <name>\t<hint1>\t<hint2>
        # where hint1/hint2/etc. are optional auxiliary information that will
        # be displayed in italics to the right of the name.
        def annotation_from_completion(completion):
            return "\t".join(
                filter(lambda x: x is not None, 
                    map(completion.get, 
                        ["name", "type", "definedIn"])))

        annotations = map(annotation_from_completion, self.returned_completions)
        names       = map(lambda x: x.get("name"),    self.returned_completions)

        annotated_completions = zip(annotations, names)
        print("Returning: " + str(annotated_completions))
        return list(annotated_completions)


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
            print("INTERCEPTED:")
            print(completions)

            print()
            self.returned_completions = completions
        return None

class UpdateCompletionsCommand(sublime_plugin.WindowCommand):
    """
    This class only exists so that the command can be called and intercepted by
    IdeBackendAutocompleteHandler to update its completions list.
    """
    def run(self, completions):
        return None

class SendIdeBackendRequestCommand(sublime_plugin.WindowCommand):
    """
    Runs a per-window process of ide-backend-client.
    (Sublime Text uses the class name to determine the name of the command
    the class executes when called, i.e. send_ide_backend_request)
    """

    backendsByWindow = {}

    def __init__(self, window):
        super(SendIdeBackendRequestCommand, self).__init__(window)
        self.boot_ide_backend()
        
        self.run({ "request": "getSourceErrors" })

    def boot_ide_backend(self):
        """
        Start up a ide-backend-client subprocess for the window, and a thread to consume its stdout.
        """
        print("Launching HIDE in " + first_folder(self.window))
        print("Backends by window: " + str(self.backendsByWindow))
        self.backendsByWindow[self.window.id()] = "Hi!"
 
 
        self.process = subprocess.Popen(["/Users/lukexi/.cabal/bin/ide-backend-client", "cabal", "."],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=first_folder(self.window)
            )
        
        self.stdoutThread = threading.Thread(target=self.read_stdout)
        self.stdoutThread.start()
        
        # self.stderrThread = threading.Thread(target=self.read_stderr)
        # self.stderrThread.start()

    def run(self, request):
        """
        Pass a request to ide-backend-client.
        Called via run_command("send_ide_backend_request", {"request":})
        """
        if self.process:
            print("SENDING " + str(request))
            encodedString = json.JSONEncoder().encode(request) + "\n"
            self.process.stdin.write(bytes(encodedString, 'UTF-8'))
            self.process.stdin.flush()

    def read_stderr(self):
        while self.process.poll() is None:
            try:
                print("STDERR:")
                print(self.process.stderr.readline().decode('UTF-8'))
            except:
                print("stderr process ending due to exception:", str(sys.exc_info()))
                return;
        print("process ended...")

    def read_stdout(self):
        """
        Reads JSON responses from ide-backend-client and dispatch them to
        various main thread handlers.
        """
        while self.process.poll() is None:
            try:
                raw = self.process.stdout.readline().decode('UTF-8')

                data = json.loads(raw)
                
                # print(data)
                progress = data.get("progress")
                response = data.get("response")

                # Pass progress messages to the status bar
                if progress:
                    progressMessage = progress.get("parsedMsg")
                    if progressMessage:
                        sublime.status_message(progressMessage)

                # Pass autocompletion responses to the completions handler
                # (via our window command hack - see note in on_window_command)
                elif response == "getAutocompletion":
                    completions = data.get("completions")
                    if completions != None:
                        sublime.set_timeout(lambda: self.update_completions(completions), 0)

                # Pass source error responses to the error highlighter
                elif response == "getSourceErrors":
                    errors = data.get("errors")
                    if errors != None:
                        sublime.set_timeout(lambda: self.highlight_errors(errors), 0)
                else:
                    print(data)
                
            except:
                print("process ending due to exception:", str(sys.exc_info()))
                self.process.terminate()
                self.process = None
                return;
        print("process ended...")

    def update_completions(self, completions):
        self.window.run_command("update_completions", {"completions":completions})

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
            msg = error.get("msg")
            error_panel.run_command("update_error_panel", {"errors":msg})
            span = error.get("span")
            # kind = error.get("kind")
            view_and_region = view_region_from_json_span(span, self.window)

            if view_and_region:
                (view_for_error, region) = view_and_region

                print("Adding error at "+ str(span) +": " + str(msg))

                error_regions_for_view = errors_by_view_id.get(view_for_error.id(), [])
                error_regions_for_view += [region]
                errors_by_view_id[view_for_error.id()] = error_regions_for_view

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

def view_region_from_json_span(span, window):
    if span == None:
        return None
    file_path    = span.get("filePath")
    from_line    = span.get("fromLine")
    from_column  = span.get("fromColumn")
    to_line      = span.get("toLine")
    to_column    = span.get("toColumn")
    full_path    = first_folder(window) + "/" + file_path
    view         = window.find_open_file(full_path)
    if view:
        from_point = view.text_point(from_line - 1, from_column - 1)
        to_point   = view.text_point(to_line   - 1, to_column   - 1)
        region     = sublime.Region(from_point, to_point)
        return (view, region)
