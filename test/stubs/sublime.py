import uuid

current_status = ""
current_error = ""

def status_message(msg):
    global current_status
    current_status = msg

def error_message(msg):
    global current_error
    current_error = msg

def set_timeout_async(fn, delay):
    fn()

def set_timeout(fn, delay):
    fn()

def load_settings(name):
    return Settings()

class Settings():

    def add_on_change(self, key, func):
        pass

    def get(self, key, default):
        return default


class FakeWindow():

    def __init__(self, folder):
        self._folders = [folder]
        self._id = uuid.uuid4()

    def id(self):
        return self._id

    def folders(self):
        return self._folders

    def run_command(self, command, args):
        pass

    # def create_output_panel():
    #     return None

fake_windows = []

ENCODED_POSITION = 1 #flag used for window.open_file
DRAW_OUTLINED = 2 # flag used for view.add_regions

clipboard = None

def create_window(path):
    global fake_windows
    window = FakeWindow(path)
    fake_windows.append(window)
    return window

def add_window(window):
    fake_windows.append(window)

def destroy_windows():
    global fake_windows
    fake_windows = []

def set_clipboard(text):
    global clipboard
    clipboard = text

def windows():
    global fake_windows
    return fake_windows

class Region():

    def __init__(self, begin, end):
        self._begin = begin
        self._end = end

    def begin(self):
        return self._begin

    def end(self):
        return self._end
