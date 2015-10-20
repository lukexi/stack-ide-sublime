import sublime_plugin

from SublimeStackIDE.stack_ide_manager import *


class RestartStackIde(sublime_plugin.ApplicationCommand):
    """
    Restarts the StackIDE plugin.
    Useful for forcing StackIDE to pick up project changes, until we implement it properly.
    Accessible via the Command Palette (Cmd/Ctrl-Shift-p)
    as "SublimeStackIDE: Restart"
    """
    def run(self):
        StackIDEManager.reset()
