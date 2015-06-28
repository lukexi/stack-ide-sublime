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

    def boot_ide_backend(self):
      firstFolder = self.window.folders()[0]
      print("Launching Hide in " + firstFolder)

      self.process = subprocess.Popen(["/Users/lukexi/.cabal/bin/ide-backend-client", "cabal", "."],
         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
         cwd=firstFolder
         )
      
      self.stdoutThread = threading.Thread(target=self.read_stdout)
      self.stdoutThread.start()

    def read_stdout(self):
        while self.process.poll() is None:
            try:
                data = json.loads(self.process.stdout.readline().decode('UTF-8'))
                
                # print(json.loads(data))
                if data.get("progress"):
                  sublime.status_message(data["progress"]["parsedMsg"])
                
            except:
                print("process ending due to exception...")
                # sublime.set_timeout(self.boot_ide_backend, 0)
                return;
        print("process ended...")

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

