import sublime, sublime_plugin
import subprocess, os
import sys
import threading
import time
import json

def first_folder(window):
    return window.folders()[0]

def relative_view_file_name(view):
    return view.file_name().replace(first_folder(view.window()) + "/", "")


class ClearErrorPanelCommand(sublime_plugin.TextCommand):
    def run(self, edit, errors):
        self.view.erase(edit, Region(0, self.view.size()))

class UpdateErrorPanelCommand(sublime_plugin.TextCommand):
    def run(self, edit, errors):
        self.view.insert(edit, 0, str(errors) + "\n\n")

class IdeBackendSaveListener(sublime_plugin.EventListener):
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
        # print("Returning: " + str(self.returned_completions))

        def annotation_from_completion(completion):
            return "\t".join(
                filter(lambda x: x is not None, 
                    map(completion.get, 
                        ["name", "definedIn", "type"])))

        annotations = map(annotation_from_completion, self.returned_completions)
        names       = map(lambda x: x.get("name"),    self.returned_completions)

        annotated_completions = zip(annotations, names)
        print("Returning: " + str(annotated_completions))
        return list(annotated_completions)

    def on_window_command(self, window, command_name, args):
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

    def boot_ide_backend(self):
        """
        Start up a ide-backend-client subprocess for the window, and a thread to consume its stdout
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
        while self.process.poll() is None:
            try:
                raw = self.process.stdout.readline().decode('UTF-8')

                data = json.loads(raw)
                
                # print(data)
                progress = data.get("progress")
                response = data.get("response")
                if progress:
                    progressMessage = progress.get("parsedMsg")
                    if progressMessage:
                        sublime.status_message(progressMessage)
                elif response == "getAutocompletion":
                    completions = data.get("completions")
                    if completions != None:
                        sublime.set_timeout(lambda: self.update_completions(completions), 0)
                elif response == "getSourceErrors":
                    errors = data.get("errors")
                    if errors:
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
        print(completions)
        self.window.run_command("update_completions", {"completions":completions})

    def highlight_errors(self, errors):
        error_panel = self.window.create_output_panel("hide_errors")
        # error_panel.set_read_only(True)
        # error_panel.set_scratch(True)
        error_panel.run_command("clear_error_panel")
        self.window.run_command("show_panel", {"panel":"output.hide_errors"})

        for error in errors:
            msg = error.get("msg")
            error_panel.run_command("update_error_panel", {"errors":msg})
            span = error.get("span")
            # kind = error.get("kind")
            regionAndFileView = regionFromJSON(span, self.window)
            print(str(regionAndFileView))
            if regionAndFileView:
                (region, file_view) = regionAndFileView
                print("Adding error at "+ str(span) +": " + str(msg))
                file_view.add_regions(str(region), [region], "invalid", "dot", sublime.DRAW_OUTLINED)

    def run(self, request):
        """
        Called via run_command("send_ide_backend_request", {"request":})
        """
        if self.process:
            print("SENDING " + str(request))
            encodedString = json.JSONEncoder().encode(request) + "\n"
            self.process.stdin.write(bytes(encodedString, 'UTF-8'))
            self.process.stdin.flush()

    def __del__(self):
        if self.process:
            self.process.terminate()
            self.process = None

def regionFromJSON(span, window):
    if span == None:
        return None
    file_path    = span.get("filePath")
    from_line    = span.get("fromLine")
    from_column  = span.get("fromColumn")
    to_line      = span.get("toLine")
    to_column    = span.get("toColumn")
    full_path    = first_folder(window) + "/" + file_path
    file_view    = window.find_open_file(full_path)
    if file_view:
        from_point = file_view.text_point(from_line - 1, from_column - 1)
        to_point   = file_view.text_point(to_line   - 1, to_column   - 1)
        region      = sublime.Region(from_point, to_point)
        return (region, file_view)
