try:
    import sublime
except ImportError:
    from test.stubs import sublime

import subprocess, os
import sys
import threading
import json
import uuid

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from utility import first_folder, complain
from req import Req
from log import Log
from win import Win
import response as res

# Make sure Popen hides the console on Windows.
# We don't need this on other platforms
# (and it would cause an error)
CREATE_NO_WINDOW = 0
if os.name == 'nt':
    CREATE_NO_WINDOW = 0x08000000

class StackIDE:


    def __init__(self, window, settings, backend=None):
        self.window = window

        self.conts = {} # Map from uuid to response handler
        self.is_alive  = True
        self.is_active = False
        self.process   = None
        self.project_path = first_folder(window)
        (project_in, project_name) = os.path.split(self.project_path)
        self.project_name = project_name

        reset_env(settings.add_to_PATH)

        if backend is None:
            self._backend = stack_ide_start(self.project_path, self.project_name, self.handle_response)
        else: # for testing
            self._backend = backend
            self._backend.handler = self.handle_response

        self.is_active = True
        self.include_targets = set()

        # TODO: could check packages here to fix the 'project_dir must equal packagename issue'

        sublime.set_timeout_async(self.load_initial_targets, 0)


    def send_request(self, request, response_handler = None):
        """
        Associates requests with handlers and passes them on to the process.
        """
        if self._backend:
            if response_handler is not None:
                seq_id = str(uuid.uuid4())
                self.conts[seq_id] = response_handler
                request = request.copy()
                request['seq'] = seq_id

            self._backend.send_request(request)
        else:
            Log.error("Couldn't send request, no process!", request)


    def load_initial_targets(self):
        """
        Get the initial list of files to check
        """
        initial_targets = stack_ide_loadtargets(self.project_path, self.project_name)
        sublime.set_timeout(lambda: self.update_files(initial_targets), 0)


    def update_new_include_targets(self, filepaths):
        for filepath in filepaths:
            self.include_targets.add(filepath)
        return list(self.include_targets)

    def update_files(self, filenames):
        new_include_targets = self.update_new_include_targets(filenames)
        self.send_request(Req.update_session_includes(new_include_targets))
        self.send_request(Req.get_source_errors(), Win(self.window).handle_source_errors)

    def end(self):
        """
        Ask stack-ide to shut down.
        """
        Win(self.window).hide_error_panel()
        self.send_request(Req.get_shutdown())
        self.die()

    def die(self):
        """
        Mark the instance as no longer alive
        """
        self.is_alive = False
        self.is_active = False

    def handle_response(self, data):
        """
        Handles JSON responses from the backend
        """
        Log.debug("Got response: ", data)

        tag = data.get("tag")
        contents = data.get("contents")
        seq_id   = data.get("seq")

        if seq_id is not None:
            self._send_to_handler(contents, seq_id)

        elif tag == "ResponseWelcome":
            self._handle_welcome(contents)

        elif tag == "ResponseUpdateSession":
            self._handle_update_session(contents)

        elif tag == "ResponseShutdownSession":
            Log.debug("Stack-ide process has shut down")

        elif tag == "ResponseLog":
            Log.debug(contents.rstrip())

        else:
            Log.normal("Unhandled response: ", data)

    def _send_to_handler(self, contents, seq_id):
        """
        Looks up a previously registered handler for the incoming response
        """
        handler = self.conts.get(seq_id)
        del self.conts[seq_id]
        if handler is not None:
            if contents is not None:
                sublime.set_timeout(lambda:handler(contents), 0)
        else:
            Log.warning("Handler not found for seq", seq_id)


    def _handle_welcome(self, welcome):
        """
        Identifies if we support the current version of the stack ide api
        """
        expected_version = (0,1,1)
        version_got = tuple(welcome) if type(welcome) is list else welcome
        if expected_version > version_got:
            Log.error("Old stack-ide protocol:", version_got, '\n', 'Want version:', expected_version)
            complain("wrong-stack-ide-version",
                "Please upgrade stack-ide to a newer version.")
        elif expected_version < version_got:
            Log.warning("stack-ide protocol may have changed:", version_got)
        else:
            Log.debug("stack-ide protocol version:", version_got)


    def _handle_update_session(self, update_session):
        """
        Show a status message for session progress updates.
        """
        msg = res.parse_update_session(update_session)
        if msg:
            sublime.status_message(msg)


    def __del__(self):
        if self.process:
            try:
                self.process.terminate()
            except ProcessLookupError:
                # it was already done...
                pass
            finally:
                self.process = None

env = {}

def reset_env(add_to_PATH):
    global env
    env = os.environ.copy()
    if len(add_to_PATH) > 0:
        env["PATH"] = os.pathsep.join(add_to_PATH + [env.get("PATH","")])


def stack_ide_packages(project_path):
    proc = subprocess.Popen(["stack", "ide", "packages"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=project_path, env=env,
        universal_newlines=True,
        creationflags=CREATE_NO_WINDOW)
    outs, errs = proc.communicate()
    return outs.splitlines()


def stack_ide_loadtargets(project_path, package):

    Log.debug("Requesting load targets for ", package)
    proc = subprocess.Popen(["stack", "ide", "load-targets", package],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=project_path, env=env,
            universal_newlines=True,
            creationflags=CREATE_NO_WINDOW)
    outs, errs = proc.communicate()
    # TODO: check response!
    return outs.splitlines()


def stack_ide_start(project_path, package, response_handler):
    """
    Start up a stack-ide subprocess for the window, and a thread to consume its stdout.
    """

    Log.debug("Calling stack ide start with PATH:", env['PATH'] if env else os.environ['PATH'])

    process = subprocess.Popen(["stack", "ide", "start", package],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=project_path, env=env,
        creationflags=CREATE_NO_WINDOW
        )

    return JsonProcessBackend(process, response_handler)


class JsonProcessBackend:
    """
    Handles process communication with JSON.
    """
    def __init__(self, process, response_handler):
        self._process = process
        self._response_handler = response_handler
        self.stdoutThread = threading.Thread(target=self.read_stdout)
        self.stdoutThread.start()
        self.stderrThread = threading.Thread(target=self.read_stderr)
        self.stderrThread.start()

    def send_request(self, request):

        try:
            Log.debug("Sending request: ", request)
            encodedString = json.JSONEncoder().encode(request) + "\n"
            self._process.stdin.write(bytes(encodedString, 'UTF-8'))
            self._process.stdin.flush()
        except BrokenPipeError as e:
            Log.error("stack-ide unexpectedly died:",e)

            # self.die()
                # Ideally we would like to die(), so that, if the error is transient,
                # we attempt to reconnect on the next check_windows() call. The problem
                # is that the stack-ide (ide-backend, actually) is not cleaning up those
                # session.* directories and they would keep accumulating, one per second!
                # So instead we do:
            self.is_active = False


    def read_stderr(self):
        """
        Reads any errors from the stack-ide process.
        """
        while self._process.poll() is None:

            try:
                error = self._process.stderr.readline().decode('UTF-8')
                if len(error) > 0:
                    Log.warning("Stack-IDE error: ", error)
            except:
                Log.error("Stack-IDE stderr process ending due to exception: ", sys.exc_info())
                return

        Log.debug("Stack-IDE stderr process ended.")

    def read_stdout(self):
        """
        Reads JSON responses from stack-ide and dispatch them to
        various main thread handlers.
        """
        while self._process.poll() is None:
            try:
                raw = self._process.stdout.readline().decode('UTF-8')
                if not raw:
                    return

                data = None
                try:
                    data = json.loads(raw)
                except:
                    Log.debug("Got a non-JSON response: ", raw)
                    continue

                #todo: try catch ?
                self._response_handler(data)

            except:
                Log.warning("Stack-IDE stdout process ending due to exception: ", sys.exc_info())
                self._process.terminate()
                self._process = None
                return

        Log.info("Stack-IDE stdout process ended.")

