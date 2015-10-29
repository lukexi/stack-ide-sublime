import threading

try:
    import sublime
except ImportError:
    from test.stubs import sublime

from settings import Settings
from log import Log
from win import Win
from stack_ide_manager import StackIDEManager


#############################
# Plugin development utils
#############################
# Ensure existing processes are killed when we
# save the plugin to prevent proliferation of
# stack-ide session.13953 folders

watchdog = None
settings = None

def plugin_loaded():
    global watchdog, settings
    settings = load_settings()
    Log._set_verbosity(settings.verbosity)
    StackIDEManager.configure(settings)
    Win.show_popup = settings.show_popup
    watchdog = StackIDEWatchdog()

def plugin_unloaded():
    global watchdog
    watchdog.kill()
    StackIDEManager.reset()
    watchdog = None


def load_settings():
    settings_obj = sublime.load_settings("SublimeStackIDE.sublime-settings")
    settings_obj.add_on_change("_on_new_settings", on_settings_changed)
    add_to_path = settings_obj.get('add_to_PATH', [])
    return Settings(
        settings_obj.get('verbosity', 'normal'),
        add_to_path if isinstance(add_to_path, list) else [],
        settings_obj.get('show_popup', False)
    )

def on_settings_changed():
    global settings
    updated_settings = load_settings()

    if updated_settings.verbosity != settings.verbosity:
        Log._set_verbosity(updated_settings.verbosity)
    elif updated_settings.add_to_PATH != settings.add_to_PATH:
        Log.normal("Settings changed, reloading backends")
        StackIDEManager.configure(updated_settings)
        StackIDEManager.reset()
    elif updated_settings.show_popup != settings.show_popup:
        Win.show_popup = updated_settings.show_popup

    settings = updated_settings

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
        StackIDEManager.check_windows()
        self.timer = threading.Timer(1.0, self.check_for_processes)
        self.timer.start()

    def kill(self):
        self.timer.cancel()
