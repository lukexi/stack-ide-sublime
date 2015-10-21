import unittest
from unittest.mock import patch
import stack_ide_manager as manager
import stack_ide as stackide
from .mocks import mock_window, cur_dir
from .stubs import sublime
from log import Log
from settings import Settings

settings = Settings("none", [], False)


class LaunchTests(unittest.TestCase):

    # launching Stack IDE is a function that should result in a
    # Stack IDE instance (null object or live)
    # the null object should contain the reason why the launch failed.
    def setUp(self):
        Log._set_verbosity("none")


    def test_launch_window_without_folder(self):
        instance = manager.configure_instance(mock_window([]), settings)
        self.assertIsInstance(instance, manager.NoStackIDE)
        self.assertRegex(instance.reason, "No folder to monitor.*")

    def test_launch_window_with_empty_folder(self):
        instance = manager.configure_instance(
            mock_window([cur_dir + '/projects/empty_project']), settings)
        self.assertIsInstance(instance, manager.NoStackIDE)
        self.assertRegex(instance.reason, "No cabal file found.*")

    def test_launch_window_with_cabal_folder(self):
        instance = manager.configure_instance(
            mock_window([cur_dir + '/projects/cabal_project']), settings)
        self.assertIsInstance(instance, manager.NoStackIDE)
        self.assertRegex(instance.reason, "No stack.yaml in path.*")

    def test_launch_window_with_wrong_cabal_file(self):
        instance = manager.configure_instance(
            mock_window([cur_dir + '/projects/cabalfile_wrong_project']), settings)
        self.assertIsInstance(instance, manager.NoStackIDE)
        self.assertRegex(
            instance.reason, "cabalfile_wrong_project.cabal not found.*")

    @unittest.skip("Actually starts a stack ide, slow and won't work on Travis")
    def test_launch_window_with_helloworld_project(self):
        instance = manager.configure_instance(
            mock_window([cur_dir + '/projects/helloworld']), settings)
        self.assertIsInstance(instance, stackide.StackIDE)
        instance.end()

    @patch('stack_ide.boot_ide_backend', side_effect=FileNotFoundError())
    def test_launch_window_stack_not_found(self, boot_mock):
        instance = manager.configure_instance(
            mock_window([cur_dir + '/projects/helloworld']), settings)
        self.assertIsInstance(instance, manager.NoStackIDE)
        self.assertRegex(
            instance.reason, "instance init failed -- stack not found")
        self.assertRegex(sublime.current_error, "Could not find program 'stack'!")

    @patch('stack_ide.boot_ide_backend', side_effect=Exception())
    def test_launch_window_stack_not_found(self, boot_mock):
        instance = manager.configure_instance(
            mock_window([cur_dir + '/projects/helloworld']), settings)
        self.assertIsInstance(instance, manager.NoStackIDE)
        self.assertRegex(
            instance.reason, "instance init failed -- unknown error")
