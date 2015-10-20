
from SublimeStackIDE.stack_ide import *
from SublimeStackIDE.settings import *

#############################
# Plugin development utils
#############################
# Ensure existing processes are killed when we
# save the plugin to prevent proliferation of
# stack-ide session.13953 folders

watchdog = None
def plugin_loaded():
    global watchdog
    watchdog = StackIDEWatchdog()

def plugin_unloaded():
    global watchdog
    watchdog.kill()
    StackIDE.reset()
    Log.reset()
    Settings.reset()
    watchdog = None


class StackIDEWatchdog():
    """
    Since I can't find any way to detect if a window closes,
    we use a watchdog timer to clean up stack-ide instances
    once we see that the window is no longer in existence.
    """
    def __init__(self):
        super(StackIDEWatchdog, self).__init__()
        Log.normal("Starting stack-ide-sublime watchdog")
        self.check_for_processes()

    def check_for_processes(self):
        StackIDE.check_windows()
        self.timer = threading.Timer(1.0, self.check_for_processes)
        self.timer.start()

    def kill(self):
        self.timer.cancel()
