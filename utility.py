import glob
import os
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

def get_keypath(a_dict, keypath):
    """
    Extracts a keypath from a nested dictionary, e.g.
    >>> get_keypath({"hey":{"there":"kid"}}, ["hey", "there"])
    'kid'
    Returns None if the keypath doesn't exist.
    """
    value = a_dict
    path = keypath
    while value and path:
        if not type(value) is dict: return None
        value = value.get(path[0])
        path = path[1:]
    return value

def module_name_for_view(view):
    module_name = view.substr(view.find("^module [A-Za-z._]*", 0)).replace("module ", "")
    return module_name

def filter_enclosing(from_col, to_col, from_line, to_line, spans):
    return [span for span in spans if
        (   ((span[1].get("spanFromLine")<from_line) or
            (span[1].get("spanFromLine") == from_line and
             span[1].get("spanFromColumn") <= from_col))
        and ((span[1].get("spanToLine")>to_line) or
            (span[1].get("spanToLine") == to_line and
             span[1].get("spanToColumn") >= to_col))
        )]

def type_info_for_sel(view,types):
    """
    Takes the type spans returned from a get_exp_types request and returns a
    tuple (type_string,type_span) of the main expression
    """
    result = None
    if view and types:
        region = view.sel()[0]
        (from_line_, from_col_) = view.rowcol(region.begin())
        (to_line_, to_col_) = view.rowcol(region.end())
        [type_string, type_span] = filter_enclosing(
            from_col_+1, to_col_+1,
            from_line_+1, to_line_+1,
            types)[0]
        result = (type_string, type_span)
    return result
