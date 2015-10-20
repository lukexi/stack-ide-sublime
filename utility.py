import glob
import os
try:
    import sublime
except ImportError:
    from test.stubs import sublime

import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from log import Log

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

def get_window(view_or_window):
    """
    Accepts a View or a Window and returns the Window
    """
    return view_or_window.window() if hasattr(view_or_window, 'window') else view_or_window

def span_from_view_selection(view):
    return span_from_view_region(view, view.sel()[0])

def view_region_from_span(view, span):
    """
    Maps a SourceSpan to a Region for a given view.

    :param sublime.View view: The view to create regions for
    :param SourceSpan span: The span to map to a region
    :rtype sublime.Region: The created Region

    """
    from_point = view.text_point(span.fromLine - 1, span.fromColumn - 1)
    to_point = view.text_point(span.toLine - 1, span.toColumn - 1)
    return sublime.Region(from_point, to_point)

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
