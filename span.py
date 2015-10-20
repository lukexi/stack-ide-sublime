from SublimeStackIDE.utility import *
import sublime

class Span:
    """
    Represents the Stack-IDE 'span' type
    """

    class InView:
        """
        When a span corresponds to a file being displayed in a view,
        this object holds the position of the span inside that view.
        """

        def __init__(self, view, from_point, to_point, region):
            self.view           = view
            self.from_point     = from_point
            self.to_point       = to_point
            self.region         = region

    @classmethod
    def from_json(cls, span, window):
        file_path    = span.get("spanFilePath")
        if file_path == None:
            return None
        from_line    = span.get("spanFromLine")
        from_column  = span.get("spanFromColumn")
        to_line      = span.get("spanToLine")
        to_column    = span.get("spanToColumn")

        full_path    = first_folder(window) + "/" + file_path
        view         = window.find_open_file(full_path)
        if view is None:
            in_view = None
        else:
            from_point = view.text_point(from_line - 1, from_column - 1)
            to_point   = view.text_point(to_line   - 1, to_column   - 1)
            region     = sublime.Region(from_point, to_point)

            in_view    = Span.InView(view, from_point, to_point, region)

        return Span(from_line, from_column, to_line, to_column, full_path, in_view)

    def __init__(self, from_line, from_column, to_line, to_column, full_path, in_view):
        self.from_line      = from_line
        self.from_column    = from_column
        self.to_line        = to_line
        self.to_column      = to_column
        self.full_path      = full_path
        self.in_view        = in_view

    def as_error_message(self, error):
        kind      = error.get("errorKind")
        error_msg = error.get("errorMsg")

        return "{file}:{from_line}:{from_column}: {kind}:\n{msg}".format(
            file=self.full_path,
            from_line=self.from_line,
            from_column=self.from_column,
            kind=kind,
            msg=error_msg)
