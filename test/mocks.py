import os
from unittest.mock import Mock, MagicMock

from stack_ide import StackIDE
from stack_ide_manager import StackIDEManager
from .fakebackend import FakeBackend
from settings import Settings

cur_dir = os.path.dirname(os.path.realpath(__file__))
test_settings = Settings("none", [], False)

def mock_window(paths=[]):
    window = MagicMock()
    window.folders = Mock(return_value=paths)
    window.id = Mock(return_value=1234)
    window.run_command = Mock(return_value=None)
    return window

def mock_view(file_path, window):
    view = MagicMock()
    view.file_name = Mock(return_value=os.path.join(window.folders()[0], file_path))
    view.match_selector = Mock(return_value=True)
    window.active_view = Mock(return_value=view)
    window.find_open_file = Mock(return_value=view)
    window.views = Mock(return_value=[view])
    view.window = Mock(return_value=window)
    region = MagicMock()
    region.begin = Mock(return_value=4)
    region.end = Mock(return_value=4)
    view.sel = Mock(return_value=[region])
    view.rowcol = Mock(return_value=(0, 0))
    view.text_point = Mock(return_value=4)
    return view

def setup_fake_backend(window, responses={}):
    backend = FakeBackend(responses)
    instance = StackIDE(window, test_settings, backend)
    backend.handler = instance.handle_response
    StackIDEManager.ide_backend_instances[
        window.id()] = instance
    return backend

def setup_mock_backend(window):
    backend = MagicMock()
    instance = StackIDE(window, test_settings, backend)
    # backend.handler = instance.handle_response
    StackIDEManager.ide_backend_instances[
        window.id()] = instance
    return backend


def default_mock_window():
    """
    Returns a (window, view) tuple pointing to /projects/helloworld/src/Main.hs
    """
    window = mock_window([cur_dir + '/projects/helloworld'])
    view = mock_view('src/Main.hs', window)
    return (window, view)
