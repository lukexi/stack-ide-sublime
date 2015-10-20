import unittest
from test.mocks import mock_view, mock_window, cur_dir
import utility

class UtilTests(unittest.TestCase):

    def test_get_relative_filename(self):
        window = mock_window([cur_dir + '/projects/helloworld'])
        view = mock_view('src/Main.hs', window)
        self.assertEqual('src/Main.hs', utility.relative_view_file_name(view))
