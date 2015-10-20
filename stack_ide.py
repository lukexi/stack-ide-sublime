import sublime, sublime_plugin
import subprocess, os
import sys
import threading
import time
import traceback
import json
import uuid

from SublimeStackIDE.settings import *
from SublimeStackIDE.span import *
from SublimeStackIDE.utility import *
from SublimeStackIDE.req import *
from SublimeStackIDE.log import *


class StackIDE:
    

    def __init__(self, window):
        self.window = window
        self.conts = {} # Map from uuid to response handler
        self.is_alive  = True
        self.is_active = False
        self.process   = None
        self.boot_ide_backend()
        self.is_active = True
        self.include_targets = set()

    def update_new_include_targets(self, filepaths):
        for filepath in filepaths:
            self.include_targets.add(filepath)
        return list(self.include_targets)

    def send_request(self, request, response_handler = None):
        if self.process:
            if response_handler is not None:
                seq_id = str(uuid.uuid4())
                self.conts[seq_id] = response_handler
                request = request.copy()
                request['seq'] = seq_id

            try:
                Log.debug("Sending request: ", request)
                encodedString = json.JSONEncoder().encode(request) + "\n"
                self.process.stdin.write(bytes(encodedString, 'UTF-8'))
                self.process.stdin.flush()
            except BrokenPipeError as e:
                Log.error("stack-ide unexpectedly died:",e)

                # self.die()
                    # Ideally we would like to die(), so that, if the error is transient,
                    # we attempt to reconnect on the next check_windows() call. The problem
                    # is that the stack-ide (ide-backend, actually) is not cleaning up those
                    # session.* directories and they would keep accumulating, one per second!
                    # So instead we do:
                self.is_active = False
        else:
            Log.error("Couldn't send request, no process!", request)

    def boot_ide_backend(self):
        """
        Start up a stack-ide subprocess for the window, and a thread to consume its stdout.
        """
        Log.normal("Launching stack-ide instance for ", first_folder(self.window))

        # Assumes the library target name is the same as the project dir
        (project_in, project_name) = os.path.split(first_folder(self.window))

        # load_targets_raw = subprocess.check_output(["stack", "ide", "load-targets", project_name])
        # load_targets = load_targets.splitlines()

        # Extend the search path if indicated
        alt_env = os.environ.copy()
        add_to_PATH = Settings.add_to_PATH()
        if len(add_to_PATH) > 0:
          alt_env["PATH"] = os.pathsep.join(add_to_PATH + [alt_env.get("PATH","")])

        Log.debug("Calling stack with PATH:", alt_env['PATH'] if alt_env else os.environ['PATH'])

        self.process = subprocess.Popen(["stack", "ide", "start", project_name],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=first_folder(self.window), env=alt_env
            )

        self.stdoutThread = threading.Thread(target=self.read_stdout)
        self.stdoutThread.start()

        self.stderrThread = threading.Thread(target=self.read_stderr)
        self.stderrThread.start()

    def end(self):
        """
        Ask stack-ide to shut down.
        """
        self.send_request({"tag":"RequestShutdownSession", "contents":[]})
        self.die()

    def die(self):
        """
        Mark the instance as no longer alive
        """
        self.is_alive = False
        self.is_active = False


    def read_stderr(self):
        """
        Reads any errors from the stack-ide process.
        """
        while self.process.poll() is None:
            try:
                Log.warning("Stack-IDE error: ", self.process.stderr.readline().decode('UTF-8'))
            except:
                Log.error("Stack-IDE stderr process ending due to exception: ", sys.exc_info())
                return;
        Log.normal("Stack-IDE stderr process ended.")

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


                data = None
                try:
                    data = json.loads(raw)
                except:
                    Log.debug("Got a non-JSON response: ", raw)
                    continue

                Log.debug("Got response: ", data)

                response = data.get("tag")
                contents = data.get("contents")
                seq_id   = data.get("seq")

                if seq_id is not None:
                    handler = self.conts.get(seq_id)
                    del self.conts[seq_id]
                    if handler is not None:
                        if contents is not None:
                            sublime.set_timeout(lambda:handler(contents), 0)
                    else:
                        Log.warning("Handler not found for seq", seq_id)

                # Check that stack-ide talks a version of the protocal we understand
                elif response == "ResponseWelcome":
                    expected_version = (0,1,1)
                    version_got = tuple(contents) if type(contents) is list else contents
                    if expected_version > version_got:
                        Log.error("Old stack-ide protocol:", version_got, '\n', 'Want version:', expected_version)
                        StackIDE.complain("wrong-stack-ide-version",
                            "Please upgrade stack-ide to a newer version.")
                    elif expected_version < version_got:
                        Log.warning("stack-ide protocol may have changed:", version_got)
                    else:
                        Log.debug("stack-ide protocol version:", version_got)

                # Pass progress messages to the status bar
                elif response == "ResponseUpdateSession":
                    if contents != None:
                        progressMessage = contents.get("progressParsedMsg")
                        if progressMessage:
                            sublime.status_message(progressMessage)

                else:
                    Log.normal("Unhandled response: ", data)

            except:
                Log.warning("Stack-IDE stdout process ending due to exception: ", sys.exc_info())
                self.process.terminate()
                self.process = None
                return;
        Log.normal("Stack-IDE stdout process ended.")

    def __del__(self):
        if self.process:
            try:
                self.process.terminate()
            except ProcessLookupError:
                # it was already done...
                pass
            finally:
                self.process = None



