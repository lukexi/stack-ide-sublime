#############################################
# PARSING
#
# see: https://github.com/commercialhaskell/stack-ide/blob/master/stack-ide-api/src/Stack/Ide/JsonAPI.hs
# and: https://github.com/fpco/ide-backend/blob/master/ide-backend-common/IdeSession/Types/Public.hs
# Types of responses:
# ResponseGetSourceErrors [SourceError]
# ResponseGetLoadedModules [ModuleName]
# ResponseGetSpanInfo [ResponseSpanInfo]
# ResponseGetExpTypes [ResponseExpType]
# ResponseGetAnnExpTypes [ResponseAnnExpType]
# ResponseGetAutocompletion [IdInfo]
# ResponseUpdateSession
# ResponseLog

def parse_autocompletions(contents):
    """
    Converts ResponseGetAutoCompletion content into [(IdProp, IdScope)]
    """
    return ((parse_idprop(item.get('idProp')),
            parse_idscope(item.get('idScope'))) for item in contents)


def parse_update_session(contents):
    """
    Converts a ResponseUpdateSession message to a single status string
    """
    tag = contents.get('tag')
    if tag == "UpdateStatusProgress":
        progress = contents.get('contents')
        return str(progress.get("progressParsedMsg"))
    elif tag == "UpdateStatusDone":
        return " "
    elif tag == "UpdateStatusRequiredRestart":
        return "Starting session..."


def parse_source_errors(contents):
    """
    Converts ResponseGetSourceErrors content into an array of SourceError objects
    """
    return (SourceError(item.get('errorKind'),
                        item.get('errorMsg'),
                        parse_either_span(item.get('errorSpan'))) for item in contents)


def parse_exp_types(contents):
    """
    Converts ResponseGetExpTypes contents into an array of pairs containing
    Text and SourceSpan
    Also see: type_info_for_sel (replace)
    """
    return ((item[0], parse_source_span(item[1])) for item in contents)


def parse_span_info_response(contents):
    """
    Converts ResponseGetSpanInfo contents into an array of pairs of SpanInfo and SourceSpan objects
    ResponseGetSpanInfo's contents are an array of SpanInfo and SourceSpan pairs
    """
    return ((parse_span_info(responseSpanInfo[0]),
             parse_source_span(responseSpanInfo[1])) for responseSpanInfo in contents)


def parse_span_info(json):
    """
    Converts SpanInfo contents into a pair of IdProp and IdScope objects

    :param dict json: responds to a Span type from Stack IDE

    SpanInfo is either 'tag' SpanId or 'tag' SpanQQ, with an nested under as contents IdInfo
    TODO: deal with SpanQQ here
    """
    contents = json.get('contents')
    return (parse_idprop(contents.get('idProp')),
            parse_idscope(contents.get('idScope')))


def parse_idprop(values):
    """
    Converts idProp content into an IdProp object.
    """
    return IdProp(values.get('idDefinedIn').get('moduleName'),
                    values.get('idDefinedIn').get('modulePackage').get('packageName'),
                    values.get('idType'),
                    values.get('idName'),
                    parse_either_span(values.get('idDefSpan')))


def parse_idscope(values):
    """
    Converts idScope content into an IdScope object (containing only an IdImportedFrom)
    """
    importedFrom = values.get('idImportedFrom')
    return IdScope(IdImportedFrom(importedFrom.get('moduleName'),
                                  importedFrom.get('modulePackage').get('packageName'))) if importedFrom else None


def parse_either_span(json):
    """
    Checks EitherSpan content and returns a SourceSpan if possible.
    """
    if json.get('tag') == 'ProperSpan':
        return parse_source_span(json.get('contents'))
    else:
        return None


def parse_source_span(json):
    """
    Converts json into a SourceSpan
    """
    paths = ['spanFilePath', 'spanFromLine', 'spanFromColumn', 'spanToLine', 'spanToColumn']
    fields = get_paths(paths, json)
    return SourceSpan(*fields) if fields else None


def get_paths(paths, values):
    """
    Converts a list of keypaths into an array of values from a dict
    """
    return list(values.get(path) for path in paths)


class SourceError():

    def __init__(self, kind, message, span):
        self.kind = kind
        self.msg = message
        self.span = span

    def __repr__(self):
        if self.span:
            return "{file}:{from_line}:{from_column}: {kind}:\n{msg}".format(
                file=self.span.filePath,
                from_line=self.span.fromLine,
                from_column=self.span.fromColumn,
                kind=self.kind,
                msg=self.msg)
        else:
            return self.msg


class SourceSpan():

    def __init__(self, filePath, fromLine, fromColumn, toLine, toColumn):
        self.filePath = filePath
        self.fromLine = fromLine
        self.fromColumn = fromColumn
        self.toLine = toLine
        self.toColumn = toColumn


class IdScope():

    def __init__(self, importedFrom):
        self.importedFrom = importedFrom


class IdImportedFrom():

    def __init__(self, module, package):
        self.module = module
        self.package = package


class IdProp():

    def __init__(self, package, module, type, name, defSpan):
        self.package = package
        self.module = module
        self.type = type
        self.name = name
        self.defSpan = defSpan
