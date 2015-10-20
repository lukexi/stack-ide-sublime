import sublime_plugin
from SublimeStackIDE.stack_ide import *

class UpdateCompletionsCommand(sublime_plugin.WindowCommand):
    """
    This class only exists so that the command can be called and intercepted by
    StackIDEAutocompleteHandler to update its completions list.
    """
    def run(self, completions):
        return None

class SendStackIdeRequestCommand(sublime_plugin.WindowCommand):
    """
    Allows sending commands via
    window.run_command("send_stack_ide_request", {"request":{"my":"request"}})
    (Sublime Text uses the class name to determine the name of the command
    the class executes when called)
    """

    def __init__(self, window):
        super(SendStackIdeRequestCommand, self).__init__(window)

    def run(self, request):
        """
        Pass a request to stack-ide.
        Called via run_command("send_stack_ide_request", {"request":})
        """
        instance = StackIDE.for_window(self.window)
        if instance:
            instance.send_request(request)

