import sublime_plugin
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from stack_ide_manager import StackIDEManager


class RestartStackIde(sublime_plugin.ApplicationCommand):
    """
    Restarts the StackIDE plugin.
    Useful for forcing StackIDE to pick up project changes, until we implement it properly.
    Accessible via the Command Palette (Cmd/Ctrl-Shift-p)
    as "SublimeStackIDE: Restart"
    """
    def run(self):
        StackIDEManager.reset()
