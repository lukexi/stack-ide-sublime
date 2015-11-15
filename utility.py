import glob
import os
try:
    import sublime
except ImportError:
    from test.stubs import sublime

import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from log import Log

complaints_shown = set()
def complain(id, text):
    """
    Show the msg as an error message (on a modal pop-up). The complaint_id is
    used to decide when we have already complained about something, so that
    we don't do it again (until reset)
    """
    if id not in complaints_shown:
        complaints_shown.add(id)
        sublime.error_message(text)

def reset_complaints():
    global complaints_shown
    complaints_shown = set()


def first_folder(window):
    """
    We only support running one stack-ide instance per window currently,
    on the first folder open in that window.
    """
    if len(window.folders()):
        return window.folders()[0]
    else:
        Log.normal("Couldn't find a folder for stack-ide-sublime")
        return None

def has_cabal_file(project_path):
    """
    Check if a cabal file exists in the project folder
    """
    files = glob.glob(os.path.join(project_path, "*.cabal"))
    return len(files) > 0

def expected_cabalfile(project_path):
    """
    The cabalfile should have the same name as the directory it resides in (stack ide limitation?)
    """
    (_, project_name) = os.path.split(project_path)
    return os.path.join(project_path, project_name + ".cabal")

def is_stack_project(project_path):
    """
    Determine if a stack.yaml exists in the given directory.
    """
    return os.path.isfile(os.path.join(project_path, "stack.yaml"))

def relative_view_file_name(view):
    """
    ide-backend expects file names as relative to the cabal project root
    """
    return view.file_name().replace(first_folder(view.window()) + "/", "")

def span_from_view_selection(view):
    return span_from_view_region(view, view.sel()[0])

def within(smaller, larger):
    return smaller.begin() >= larger.begin() and smaller.end() <= larger.end()

def filter_enclosing(view, region, span_pairs):
    return ((item, span) for item, span in span_pairs if within(region, view_region_from_span(view, span)))

def format_type(raw_type):
    words = raw_type.replace("(", " ( ").replace("[", " [ ").split(' ')
    return (" ".join(map(format_subtype, words)).replace(" ( ","(").replace(" [ ","["))

def format_subtype(type_string):
    # See documentation about popups here:
    #       http://facelessuser.github.io/sublime-markdown-popups/usage/ (official doc)
    # and   https://www.sublimetext.com/forum/viewtopic.php?f=2&t=17583  (html support announcment)

    words = [x for x in type_string.split('.') if x != '']
    # [x for x in type_string.split('.') is necessary to handle the `a.` part of `forall a.` properly

    if (len(words) > 1):
        s = ("_"+words[-1])
    else:
        s = type_string

    if s == "->":
        return ('<span style="color: blue">{0}</span>'.format("->"))
    elif s == "(" or s == ")" or s == "[" or s == "]" or s=='':
        return s
    elif (s[0] != '_' and s[0].islower()):
        return ('<span style="color: #4C4C4C">{0}</span>'.format(s))
    else:
        return ('<a href="http://www.stackage.org/lts/hoogle?q={0}" style="color: #333333">{1}</a>'.format(type_string, s))

def is_haskell_view(view):
    return view.match_selector(view.sel()[0].begin(), "source.haskell")

def view_region_from_span(view, span):
    """
    Maps a SourceSpan to a Region for a given view.

    :param sublime.View view: The view to create regions for
    :param SourceSpan span: The span to map to a region
    :rtype sublime.Region: The created Region

    """
    return sublime.Region(
        view.text_point(span.fromLine - 1, span.fromColumn - 1),
        view.text_point(span.toLine - 1, span.toColumn - 1))

def span_from_view_region(view, region):
    (from_line, from_col) = view.rowcol(region.begin())
    (to_line,   to_col)   = view.rowcol(region.end())
    return {
        "spanFilePath": relative_view_file_name(view),
        "spanFromLine": from_line + 1,
        "spanFromColumn": to_col + 1,
        "spanToLine": to_line + 1,
        "spanToColumn": to_col + 1
        }
