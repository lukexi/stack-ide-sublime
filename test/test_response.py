import unittest
import response as res

source_errors = {'seq': 'd0599c00-0b77-441c-8947-b3882cab298c', 'tag': 'ResponseGetSourceErrors', 'contents': [{'errorSpan': {'tag': 'ProperSpan', 'contents': {'spanFromColumn': 22, 'spanFromLine': 11, 'spanFilePath': 'src/Lib.hs', 'spanToColumn': 28, 'spanToLine': 11}}, 'errorKind': 'KindError', 'errorMsg': 'Couldn\'t match expected type ‘Integer’ with actual type ‘[Char]’\nIn the first argument of ‘greet’, namely ‘"You!"’\nIn the second argument of ‘($)’, namely ‘greet "You!"’\nIn a stmt of a \'do\' block: putStrLn $ greet "You!"'}, {'errorSpan': {'tag': 'ProperSpan', 'contents': {'spanFromColumn': 24, 'spanFromLine': 15, 'spanFilePath': 'src/Lib.hs', 'spanToColumn': 25, 'spanToLine': 15}}, 'errorKind': 'KindError', 'errorMsg': 'Couldn\'t match expected type ‘[Char]’ with actual type ‘Integer’\nIn the second argument of ‘(++)’, namely ‘s’\nIn the expression: "Hello, " ++ s'}]}
many_completions = {'tag': 'ResponseGetAutocompletion', 'contents': [{'idProp': {'idSpace': 'VarName', 'idDefinedIn': {'moduleName': 'GHC.List', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idHomeModule': {'moduleName': 'GHC.OldList', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idType': None, 'idName': '!!', 'idDefSpan': {'tag': 'TextSpan', 'contents': '<no location info>'}}, 'idScope': {'tag': 'Imported', 'idImportedFrom': {'moduleName': 'Data.List', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idImportSpan': {'tag': 'ProperSpan', 'contents': {'spanFilePath': 'app/Main.hs', 'spanFromLine': 4, 'spanToLine': 4, 'spanFromColumn': 1, 'spanToColumn': 17}}, 'idImportQual': ''}}, {'idProp': {'idSpace': 'VarName', 'idDefinedIn': {'moduleName': 'GHC.Base', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idHomeModule': {'moduleName': 'Data.Function', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idType': '(a -> b) -> a -> b', 'idName': '$', 'idDefSpan': {'tag': 'TextSpan', 'contents': '<wired into compiler>'}}, 'idScope': {'tag': 'WiredIn', 'contents': []}}, {'idProp': {'idSpace': 'VarName', 'idDefinedIn': {'moduleName': 'GHC.Base', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idHomeModule': {'moduleName': 'Prelude', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idType': None, 'idName': '$!', 'idDefSpan': {'tag': 'TextSpan', 'contents': '<no location info>'}}, 'idScope': {'tag': 'Imported', 'idImportedFrom': {'moduleName': 'Prelude', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idImportSpan': {'tag': 'ProperSpan', 'contents': {'spanFilePath': 'app/Main.hs', 'spanFromLine': 1, 'spanToLine': 1, 'spanFromColumn': 1, 'spanToColumn': 1}}, 'idImportQual': ''}}, {'idProp': {'idSpace': 'VarName', 'idDefinedIn': {'moduleName': 'GHC.Classes', 'modulePackage': {'packageName': 'ghc-prim', 'packageKey': 'ghc-prim', 'packageVersion': '0.4.0.0'}}, 'idHomeModule': {'moduleName': 'Data.Bool', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idType': None, 'idName': '&&', 'idDefSpan': {'tag': 'TextSpan', 'contents': '<no location info>'}}, 'idScope': {'tag': 'Imported', 'idImportedFrom': {'moduleName': 'Prelude', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idImportSpan': {'tag': 'ProperSpan', 'contents': {'spanFilePath': 'app/Main.hs', 'spanFromLine': 1, 'spanToLine': 1, 'spanFromColumn': 1, 'spanToColumn': 1}}, 'idImportQual': ''}}, {'idProp': {'idSpace': 'VarName', 'idDefinedIn': {'moduleName': 'GHC.Num', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idHomeModule': {'moduleName': 'Prelude', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idType': None, 'idName': '*', 'idDefSpan': {'tag': 'TextSpan', 'contents': '<no location info>'}}, 'idScope': {'tag': 'Imported', 'idImportedFrom': {'moduleName': 'Prelude', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idImportSpan': {'tag': 'ProperSpan', 'contents': {'spanFilePath': 'app/Main.hs', 'spanFromLine': 1, 'spanToLine': 1, 'spanFromColumn': 1, 'spanToColumn': 1}}, 'idImportQual': ''}}, {'idProp': {'idSpace': 'VarName', 'idDefinedIn': {'moduleName': 'GHC.Float', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idHomeModule': {'moduleName': 'Prelude', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idType': None, 'idName': '**', 'idDefSpan': {'tag': 'TextSpan', 'contents': '<no location info>'}}, 'idScope': {'tag': 'Imported', 'idImportedFrom': {'moduleName': 'Prelude', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idImportSpan': {'tag': 'ProperSpan', 'contents': {'spanFilePath': 'app/Main.hs', 'spanFromLine': 1, 'spanToLine': 1, 'spanFromColumn': 1, 'spanToColumn': 1}}, 'idImportQual': ''}}, {'idProp': {'idSpace': 'VarName', 'idDefinedIn': {'moduleName': 'GHC.Base', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idHomeModule': {'moduleName': 'Control.Applicative', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idType': None, 'idName': '*>', 'idDefSpan': {'tag': 'TextSpan', 'contents': '<no location info>'}}, 'idScope': {'tag': 'Imported', 'idImportedFrom': {'moduleName': 'Prelude', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idImportSpan': {'tag': 'ProperSpan', 'contents': {'spanFilePath': 'app/Main.hs', 'spanFromLine': 1, 'spanToLine': 1, 'spanFromColumn': 1, 'spanToColumn': 1}}, 'idImportQual': ''}}, {'idProp': {'idSpace': 'VarName', 'idDefinedIn': {'moduleName': 'GHC.Num', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idHomeModule': {'moduleName': 'Prelude', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idType': None, 'idName': '+', 'idDefSpan': {'tag': 'TextSpan', 'contents': '<no location info>'}}, 'idScope': {'tag': 'Imported', 'idImportedFrom': {'moduleName': 'Prelude', 'modulePackage': {'packageName': 'base', 'packageKey': 'base', 'packageVersion': '4.8.1.0'}}, 'idImportSpan': {'tag': 'ProperSpan', 'contents': {'spanFilePath': 'app/Main.hs', 'spanFromLine': 1, 'spanToLine': 1, 'spanFromColumn': 1, 'spanToColumn': 1}}, 'idImportQual': ''}}]}
readFile_exp_types = {'tag': 'ResponseGetExpTypes', 'contents': [['FilePath -> IO String', {'spanToColumn': 25, 'spanToLine': 10, 'spanFromColumn': 17, 'spanFromLine': 10, 'spanFilePath': 'src/Lib.hs'}], ['IO String', {'spanToColumn': 36, 'spanToLine': 10, 'spanFromColumn': 17, 'spanFromLine': 10, 'spanFilePath': 'src/Lib.hs'}], ['IO ()', {'spanToColumn': 28, 'spanToLine': 11, 'spanFromColumn': 12, 'spanFromLine': 9, 'spanFilePath': 'src/Lib.hs'}]], 'seq': 'fd3eb2a5-e390-4ad7-be72-8b2e82441a95'}
status_progress_restart = {'contents': {'contents': [], 'tag': 'UpdateStatusRequiredRestart'}, 'tag': 'ResponseUpdateSession'}
status_progress_1 = {'contents': {'contents': {'progressParsedMsg': 'Compiling Lib', 'progressNumSteps': 2, 'progressStep': 1, 'progressOrigMsg': '[1 of 2] Compiling Lib              ( /Users/tomv/Projects/Personal/haskell/helloworld/src/Lib.hs, interpreted )'}, 'tag': 'UpdateStatusProgress'}, 'tag': 'ResponseUpdateSession'}
status_progress_2 = {'contents': {'contents': {'progressParsedMsg': 'Compiling Main', 'progressNumSteps': 2, 'progressStep': 2, 'progressOrigMsg': '[2 of 2] Compiling Main             ( /Users/tomv/Projects/Personal/haskell/helloworld/app/Main.hs, interpreted )'}, 'tag': 'UpdateStatusProgress'}, 'tag': 'ResponseUpdateSession'}
status_progress_done = {'contents': {'contents': [], 'tag': 'UpdateStatusDone'}, 'tag': 'ResponseUpdateSession'}


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
