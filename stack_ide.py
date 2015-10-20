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



def send_request(view_or_window, request, on_response = None):
    """
    Sends the given request to the (view's) window's stack-ide instance,
    optionally handling its response
    """
    window = get_window(view_or_window)
    if StackIDE.is_running(window):
        StackIDE.for_window(window).send_request(request, on_response)


class StackIDE:
    ide_backend_instances = {}
    complaints_shown = set()

    

    @classmethod
    def check_windows(cls):
        """
        Compares the current windows with the list of instances:
          - new windows are assigned a process of stack-ide each
          - stale processes are stopped

        NB. This is the only method that updates ide_backend_instances,
        so as long as it is not called concurrently, there will be no
        race conditions...
        """
        current_windows = {w.id(): w for w in sublime.windows()}
        updated_instances = {}

        # Kill stale instances, keep live ones
        for win_id,instance in StackIDE.ide_backend_instances.items():
            if win_id not in current_windows:
                # This is a window that is now closed, we may need to kill its process
                if instance.is_active:
                    Log.normal("Stopping stale process for window", win_id)
                    instance.end()
            else:
                # This window is still active. There are three possibilities:
                #  1) it has an alive and active instance.
                #  2) it has an alive but inactive instance (one that failed to init, etc)
                #  3) it has a dead instance, i.e., one that was killed.
                #
                # A window with a dead instances is treated like a new one, so we will
                # try to launch a new instance for it
                if instance.is_alive:
                    del current_windows[win_id]
                    updated_instances[win_id] = instance

        StackIDE.ide_backend_instances = updated_instances

        # Thw windows remaining in current_windows are new, so they have no instance.
        # We try to create one for them
        for window in current_windows.values():
            folder = first_folder(window)

            if not folder:
                # Make sure there is a folder to monitor
                Log.normal("No folder to monitor for window ", window.id())
                instance = NoStackIDE("window folder not being monitored")

            elif not has_cabal_file(folder):

                Log.normal("No cabal file found in ", folder)
                instance = NoStackIDE("window folder not being monitored")

            elif not os.path.isfile(expected_cabalfile(folder)):

                Log.warning("Expected cabal file", expected_cabalfile(folder), "not found")
                instance = NoStackIDE("window folder not being monitored")

            elif not is_stack_project(folder):

                Log.warning("No stack.yaml in path ", folder)
                instance = NoStackIDE("window folder not being monitored")

                # TODO: We should also support single files, which should get their own StackIDE instance
                # which would then be per-view. Have a registry per-view that we check, then check the window.

            else:
                try:
                    # If everything looks OK, launch a StackIDE instance
                    Log.normal("Initializing window", window.id())
                    instance = StackIDE(window)
                except FileNotFoundError as e:
                    instance = NoStackIDE("instance init failed -- stack not found")
                    Log.error(e)
                    cls.complain('stack-not-found',
                        "Could not find program 'stack'!\n\n"
                        "Make sure that 'stack' and 'stack-ide' are both installed. "
                        "If they are not on the system path, edit the 'add_to_PATH' "
                        "setting in SublimeStackIDE  preferences." )
                except Exception:
                    instance = NoStackIDE("instance init failed -- unknown error")
                    Log.error("Failed to initialize window " + str(window.id()) + ":")
                    Log.error(traceback.format_exc())

            # Cache the instance
            StackIDE.ide_backend_instances[window.id()] = instance

            # Nothing left to do
            if isinstance(instance, NoStackIDE):
                continue

            # Kick off the process by sending an initial request. We use another thread
            # to avoid any accidental blocking....
            # def kick_off():
            #   Log.normal("Kicking off window", window.id())
            #   send_request(window,
            #     request     = Req.get_source_errors(),
            #     on_response = Win(window).highlight_errors
            #   )
            # sublime.set_timeout_async(kick_off,300)


    @classmethod
    def is_running(cls, window):
        if not window:
            return False
        return StackIDE.for_window(window) is not None


    @classmethod
    def for_window(cls, window):
        instance = StackIDE.ide_backend_instances.get(window.id())
        if instance and not instance.is_active:
            instance = None

        return instance

    @classmethod
    def kill_all(cls):
        Log.normal("Killing all stack-ide-sublime instances:", {k:str(v) for k,v in StackIDE.ide_backend_instances.items()})
        for instance in StackIDE.ide_backend_instances.values():
            instance.end()

    @classmethod
    def reset(cls):
        """
        Kill all instances, and forget about previous notifications.
        """
        Log.normal("Resetting StackIDE")
        cls.kill_all()
        cls.complaints_shown = set()


    @classmethod
    def complain(cls,complaint_id,msg):
       """
       Show the msg as an error message (on a modal pop-up). The complaint_id is
       used to decide when we have already complained about something, so that
       we don't do it again (until reset)
       """
       if complaint_id not in cls.complaints_shown:
           cls.complaints_shown.add(complaint_id)
           sublime.error_message(msg)


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
                # # Pass progress messages to the status bar
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


class NoStackIDE:
    """
    Objects of this class are used for windows that don't have an associated stack-ide process
    (e.g., because initialization failed or they are not being monitored)
    """

    def __init__(self, reason):
        self.is_alive = True
        self.is_active = False
        self.reason = reason

    def end(self):
        self.is_alive = False

    def __str__(self):
        return 'NoStackIDE(' + self.reason + ')'

