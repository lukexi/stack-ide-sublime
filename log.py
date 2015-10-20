from SublimeStackIDE.settings import *

class Log:
  """
  Logging facilities
  """

  verbosity = None

  VERB_NONE    = 0
  VERB_ERROR   = 1
  VERB_WARNING = 2
  VERB_NORMAL  = 3
  VERB_DEBUG   = 4

  @classmethod
  def reset(cls):
      Log.verbosity = None

  @classmethod
  def error(cls,*msg):
      Log._record(Log.VERB_ERROR, *msg)

  @classmethod
  def warning(cls,*msg):
      Log._record(Log.VERB_WARNING, *msg)

  @classmethod
  def normal(cls,*msg):
      Log._record(Log.VERB_NORMAL, *msg)

  @classmethod
  def debug(cls,*msg):
      Log._record(Log.VERB_DEBUG, *msg)

  @classmethod
  def _record(cls, verb, *msg):
      if not Log.verbosity:
          Log._set_verbosity()

      if verb <= Log.verbosity:
          for line in ''.join(map(lambda x: str(x), msg)).split('\n'):
              print('[SublimeStackIDE]['+cls._show_verbosity(verb)+']:',*msg)

          if verb == Log.VERB_ERROR:
              sublime.status_message('There were errors, check the console log')
          elif verb == Log.VERB_WARNING:
              sublime.status_message('There were warnings, check the console log')

  @classmethod
  def _set_verbosity(cls):
      verb = Settings.verbosity().lower()

      if verb == "none":
          Log.verbosity = Log.VERB_NONE
      elif verb == "error":
          Log.verbosity = Log.VERB_ERROR
      elif verb == "warning":
          Log.verbosity = Log.VERB_WARNING
      elif verb == "normal":
          Log.verbosity = Log.VERB_NORMAL
      elif verb == "debug":
          Log.verbosity = Log.VERB_DEBUG
      else:
          Log.verbosity = Log.VERB_WARNING
          Log.warning("Invalid verbosity: '" + str(verb) + "'")

  @classmethod
  def _show_verbosity(cls,verb):
      return ["?!","ERROR","WARN","NORM","DEBUG"][verb]
