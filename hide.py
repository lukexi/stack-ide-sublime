import sublime, sublime_plugin
import subprocess, os
import sys
import threading
import time
import json

class ExampleCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.view.insert(edit, 0, "Hello, World!")

class HideSession(sublime_plugin.WindowCommand):
    def __init__(self, something):
        super(HideSession, self).__init__(something)

        firstFolder = self.window.folders()[0]
        print("Launching Hide in " + firstFolder)

        self.process = subprocess.Popen(["/Users/lukexi/.cabal/bin/ide-backend-client", "cabal", "."],
           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
           cwd=firstFolder
           )
        
        self.stdoutThread = threading.Thread(target=self.read_stdout)
        self.stdoutThread.start()

        def foo():
          print("Calling in 5...")
          time.sleep(5)
          print("Calling!!!!!!!!!!!!!!!!!!!")
          self.process.stdin.write(bytes("""{"request":"getSourceErrors"}\n""", 'UTF-8'))
          self.process.stdin.flush()
        threading.Thread(target=foo).start()
        

    def read_stdout(self):
        while self.process.poll() is None:
            try:
                data = self.process.stdout.readline().decode('UTF-8')
                print(data)
                print(json.loads(data))
            except:
                print("process ending due to exception...")
                return;
        print("process ended...")

    def __del__(self):
        self.process.terminate()
        print(self.id, 'died')

