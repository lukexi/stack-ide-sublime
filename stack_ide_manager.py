import traceback
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from stack_ide import *
from log import Log
from utility import *
try:
    import sublime
except ImportError:
    from test.stubs import sublime

def send_request(view_or_window, request, on_response = None):
    """
    Sends the given request to the (view's) window's stack-ide instance,
    optionally handling its response
    """
    window = get_window(view_or_window)
    if StackIDEManager.is_running(window):
        StackIDEManager.for_window(window).send_request(request, on_response)

def configure_instance(window, settings):

    folder = first_folder(window)

    if not folder:
        msg = "No folder to monitor for window " + str(window.id())
        Log.normal("Window {}: {}".format(str(window.id()), msg))
        instance = NoStackIDE(msg)

    elif not has_cabal_file(folder):
        msg = "No cabal file found in " + folder
        Log.normal("Window {}: {}".format(str(window.id()), msg))
        instance = NoStackIDE(msg)

    elif not os.path.isfile(expected_cabalfile(folder)):
        msg = "Expected cabal file " + expected_cabalfile(folder) + " not found"
        Log.normal("Window {}: {}".format(str(window.id()), msg))
        instance = NoStackIDE(msg)

    elif not is_stack_project(folder):
        msg = "No stack.yaml in path " + folder
        Log.warning("Window {}: {}".format(str(window.id()), msg))
        instance = NoStackIDE(msg)

        # TODO: We should also support single files, which should get their own StackIDE instance
        # which would then be per-view. Have a registry per-view that we check, then check the window.

    else:
        try:
            # If everything looks OK, launch a StackIDE instance
            Log.normal("Initializing window", window.id())
            instance = StackIDE(window, settings)
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


    return instance


class StackIDEManager:
    ide_backend_instances = {}
    complaints_shown = set()
    settings = None

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
        for win_id,instance in StackIDEManager.ide_backend_instances.items():
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

        StackIDEManager.ide_backend_instances = updated_instances

        # Thw windows remaining in current_windows are new, so they have no instance.
        # We try to create one for them
        for window in current_windows.values():
            StackIDEManager.ide_backend_instances[window.id()] = configure_instance(window, cls.settings)


    @classmethod
    def is_running(cls, window):
        if not window:
            return False
        return StackIDEManager.for_window(window) is not None


    @classmethod
    def for_window(cls, window):
        instance = StackIDEManager.ide_backend_instances.get(window.id())
        if instance and not instance.is_active:
            instance = None

        return instance

    @classmethod
    def kill_all(cls):
        Log.normal("Killing all stack-ide-sublime instances:", {k:str(v) for k,v in StackIDEManager.ide_backend_instances.items()})
        for instance in StackIDEManager.ide_backend_instances.values():
            instance.end()

    @classmethod
    def reset(cls, settings):
        """
        Kill all instances, and forget about previous notifications.
        """
        Log.normal("Resetting StackIDE")
        cls.kill_all()
        cls.complaints_shown = set()
        cls.settings = settings

    @classmethod
    def configure(cls, settings):
        cls.settings = settings

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
