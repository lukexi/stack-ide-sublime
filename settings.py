import sublime, sublime_plugin
from SublimeStackIDE.stack_ide import *
from SublimeStackIDE.log import *

class Settings:

    # This is the sublime.Settings object associated to "SublimeStackIDE.sublime-settings".
    # The Sublime API guarantees that no matter how many times we call sublime.load_settings(),
    # we will always get the same object, so it is safe to save it (in particular, this means
    # that if the user modifies the settings, they will be reflected on this object (one can
    # then use settings.add_on_change() to register a callback, when a reaction is needed).
    settings = None

    @classmethod
    def _get(cls,key,default):
        cls.lazy_init()
        return cls.settings.get(key,default)


    @classmethod
    def lazy_init(cls):
        if cls.settings is None:
            cls.settings = sublime.load_settings("SublimeStackIDE.sublime-settings")
            cls.settings.add_on_change("_on_new_settings",Settings._on_new_settings)

    @staticmethod
    def _on_new_settings():
      Log.reset()
      StackIDE.reset()
        # Whenever the add_to_PATH setting changes, it can be that a) instances
        # that failed to be initialized since 'stack' was not found, now have a
        # chance of being functional, or b) the user wants to use another version
        # of stack / stack-ide. In any case, we start again...

    @classmethod
    def reset(cls):
      """
      Removes settings listeners
      """
      if cls.settings:
        cls.settings.clear_on_change("_on_new_settings")
        cls.settings = None

    @classmethod
    def add_to_PATH(cls):
        val = cls._get("add_to_PATH", [])
        if not isinstance(val,list):
            val = []
        return val

    @classmethod
    def show_popup(cls):
        val = cls._get("show_popup", False)
        return val

    @classmethod
    def verbosity(cls):
        return cls._get("verbosity","warning")



