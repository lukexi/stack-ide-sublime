import unittest
from test.mocks import mock_view, mock_window, cur_dir
import utility

class UtilTests(unittest.TestCase):

    def test_get_relative_filename(self):
        window = mock_window([cur_dir + '/projects/helloworld'])
        view = mock_view('src/Main.hs', window)
        self.assertEqual('src/Main.hs', utility.relative_view_file_name(view))

    def test_is_haskell_view(self):
        window = mock_window([cur_dir + '/projects/helloworld'])
        view = mock_view('src/Main.hs', window)
        self.assertTrue(utility.is_haskell_view(view))

    def test_span_from_view_selection(self):
        window = mock_window([cur_dir + '/projects/helloworld'])
        view = mock_view('src/Main.hs', window)
        span = utility.span_from_view_selection(view)
        self.assertEqual(1, span['spanFromLine'])
        self.assertEqual(1, span['spanToLine'])
        self.assertEqual(1, span['spanFromColumn'])
        self.assertEqual(1, span['spanToColumn'])
        self.assertEqual('src/Main.hs', span['spanFilePath'])
