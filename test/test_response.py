import unittest
import response as res
from .data import source_errors, status_progress_1, status_progress_2, status_progress_done, status_progress_restart, many_completions, readFile_exp_types

class ParsingTests(unittest.TestCase):

    def test_parse_source_errors_empty(self):
        errors = res.parse_source_errors([])
        self.assertEqual(0, len(list(errors)))

    def test_parse_source_errors_error(self):
        errors = list(res.parse_source_errors(source_errors.get('contents')))
        self.assertEqual(2, len(errors))
        err1, err2 = errors
        self.assertEqual(err1.kind, 'KindError')
        self.assertRegex(err1.msg, "Couldn\'t match expected type ‘Integer’")
        self.assertEqual(err1.span.filePath, 'src/Lib.hs')
        self.assertEqual(err1.span.fromLine, 11)
        self.assertEqual(err1.span.fromColumn, 22)

        self.assertEqual(err2.kind, 'KindError')
        self.assertRegex(err2.msg, "Couldn\'t match expected type ‘\[Char\]’")
        self.assertEqual(err2.span.filePath, 'src/Lib.hs')
        self.assertEqual(err2.span.fromLine, 15)
        self.assertEqual(err2.span.fromColumn, 24)

    def test_parse_exp_types_empty(self):
        exp_types = res.parse_exp_types([])
        self.assertEqual(0, len(list(exp_types)))

    def test_parse_exp_types_readFile(self):
        exp_types = list(res.parse_exp_types(readFile_exp_types.get('contents')))
        self.assertEqual(3, len(exp_types))
        (type, span) = exp_types[0]

        self.assertEqual('FilePath -> IO String', type)
        self.assertEqual('src/Lib.hs', span.filePath)

    def test_parse_completions_empty(self):
        self.assertEqual([], list(res.parse_autocompletions([])))

    def test_parse_completions(self):
        completions = list(res.parse_autocompletions(many_completions.get('contents')))
        self.assertEqual(8, len(completions))
        (prop, scope) = completions[0]
        self.assertEqual('!!', prop.name)
        self.assertEqual(None, prop.type)
        self.assertEqual('Data.List', scope.importedFrom.module)

    def test_parse_update_session(self):

        self.assertEqual('Starting session...', res.parse_update_session(status_progress_restart.get('contents')))
        self.assertEqual('Compiling Lib', res.parse_update_session(status_progress_1.get('contents')))
        self.assertEqual('Compiling Main', res.parse_update_session(status_progress_2.get('contents')))
        self.assertEqual(' ', res.parse_update_session(status_progress_done.get('contents')))
