import sublime, sublime_plugin
import subprocess, os
import sys
import threading
import time
import json

# class ExampleCommand(sublime_plugin.TextCommand):
#   def run(self, edit):
#     self.view.insert(edit, 0, "Hello, World!")

class TestRequestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print("running!")
        request = {"request":"getSourceErrors"}
        self.view.window().run_command("send_ide_backend_request", {"request":request})


class IdeBackendSaveListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        request = {
            "request":"updateSession",
            "update": [
                { "update": "updateSourceFileFromFile"
                , "filePath": view.file_name()
                }
            ]
            }
        view.window().run_command("send_ide_backend_request", {"request":request})
        request = { "request": "getSourceErrors" }
        view.window().run_command("send_ide_backend_request", {"request":request})

class IdeBackendAutocompleteHandler(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
      print("Please autocomplete: " + prefix)

class SendIdeBackendRequestCommand(sublime_plugin.WindowCommand):
    """
    Runs a per-window process of ide-backend-client.
    (Sublime Text uses the class name to determine the name of the command
    the class executes when called, i.e. send_ide_backend_request)
    """
    def __init__(self, window):
        """
        Find the main folder of the window, launch ide-backend-client in cabal mode
        with the folder as the working directory, and launch a thread to consume
        the stdout of ide-backend-client.
        """
        super(SendIdeBackendRequestCommand, self).__init__(window)
        self.boot_ide_backend()

    def first_folder(self):
      return self.window.folders()[0]

    def boot_ide_backend(self):
      
      print("Launching Hide in " + self.first_folder())

      self.process = subprocess.Popen(["/Users/lukexi/.cabal/bin/ide-backend-client", "cabal", "."],
         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
         cwd=self.first_folder()
         )
      
      self.stdoutThread = threading.Thread(target=self.read_stdout)
      self.stdoutThread.start()

    def read_stdout(self):
        while self.process.poll() is None:
            try:
                data = json.loads(self.process.stdout.readline().decode('UTF-8'))
                
                # print(json.loads(data))
                progress = data.get("progress")
                response = data.get("response")
                if progress:
                  sublime.status_message(data["progress"]["parsedMsg"])
                elif response == "getSourceErrors":
                  errors = data.get("errors")
                  if errors:
                    sublime.set_timeout(lambda: self.highlight_errors(errors), 0)
                
            except:
                print("process ending due to exception:", str(sys.exc_info()[0]))
                # sublime.set_timeout(self.boot_ide_backend, 0)
                return;
        print("process ended...")

    def highlight_errors(self, errors):
      for error in errors:
        msg = error.get("msg")
        span = error.get("span")
        kind = error.get("kind")
        if span:
          file_path   = span.get("filePath")
          from_line   = span.get("fromLine")
          from_column = span.get("fromColumn")
          to_line     = span.get("toLine")
          to_column   = span.get("toColumn")
          full_path   = self.first_folder() + "/" + file_path
          file_view   = self.window.find_open_file(full_path)
          if file_view:
            from_region = file_view.text_point(from_line - 1, from_column - 1)
            to_region   = file_view.text_point(to_line - 1, to_column - 1)
            region      = sublime.Region(from_region, to_region)
            file_view.add_regions("errors", [region], "invalid", "dot", sublime.DRAW_OUTLINED)

    def run(self, request):
        """
        Called via run_command("send_ide_backend_request", {"request":})
        """
        # request = {"request":"getSourceErrors"}
        print("SENDING " + str(request))
        encodedString = json.JSONEncoder().encode(request) + "\n"
        self.process.stdin.write(bytes(encodedString, 'UTF-8'))
        self.process.stdin.flush()

    def __del__(self):
        self.process.terminate()

