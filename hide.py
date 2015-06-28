import sublime, sublime_plugin
import subprocess, os
import sys
import threading
import time
import json

# class ExampleCommand(sublime_plugin.TextCommand):
#   def run(self, edit):
#     self.view.insert(edit, 0, "Hello, World!")

class UpdateErrorPanelCommand(sublime_plugin.TextCommand):
    def run(self, edit, errors):
        self.view.insert(edit, 0, str(errors))

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
        send_request(view, request)
        send_request(view, { "request": "getSourceErrors" })

def send_request(view, request):
  view.window().run_command("send_ide_backend_request", {"request":request})

class IdeBackendAutocompleteHandler(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
      request = {
        "request":"getAutocompletion", 
        "autocomplete": {
          "filePath": view.file_name(), 
          "prefix": prefix
          } 
        }
      send_request(view, request)

class SendIdeBackendRequestCommand(sublime_plugin.WindowCommand):
    """
    Runs a per-window process of ide-backend-client.
    (Sublime Text uses the class name to determine the name of the command
    the class executes when called, i.e. send_ide_backend_request)
    """
    def __init__(self, window):
        super(SendIdeBackendRequestCommand, self).__init__(window)
        self.boot_ide_backend()

    def first_folder(self):
      return self.window.folders()[0]

    def boot_ide_backend(self):
      """
      Start up a ide-backend-client subprocess for the window, and a thread to consume its stdout
      """
      print("Launching HIDE in " + self.first_folder())

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
                else:
                  print(data)
                
            except:
                print("process ending due to exception:", str(sys.exc_info()[0]))
                # sublime.set_timeout(self.boot_ide_backend, 0)
                return;
        print("process ended...")

    def highlight_errors(self, errors):
      error_panel = self.window.create_output_panel("hide_errors")
      # error_panel.set_read_only(True)
      # error_panel.set_scratch(True)
      self.window.run_command("show_panel", {"panel":"output.hide_errors"})

      for error in errors:
        msg = error.get("msg")
        error_panel.run_command("update_error_panel", {"errors":msg})
        span = error.get("span")
        kind = error.get("kind")
        regionAndFileView = regionFromJSON(span, self.window)
        print(str(regionAndFileView))
        if regionAndFileView:
          (region, file_view) = regionAndFileView
          file_view.add_regions(str(region), [region], "invalid", "dot", sublime.DRAW_OUTLINED)

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

def regionFromJSON(span, window):
  if span == None:
    return None
  first_folder = window.folders()[0]
  file_path    = span.get("filePath")
  from_line    = span.get("fromLine")
  from_column  = span.get("fromColumn")
  to_line      = span.get("toLine")
  to_column    = span.get("toColumn")
  full_path    = first_folder + "/" + file_path
  file_view    = window.find_open_file(full_path)
  if file_view:
    from_region = file_view.text_point(from_line - 1, from_column - 1)
    to_region   = file_view.text_point(to_line   - 1, to_column   - 1)
    region      = sublime.Region(from_region, to_region)
    return (region, file_view)
