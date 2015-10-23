from .data import exp_types_response

def seq_response(seq_id, contents):
    contents['seq']= seq_id
    return contents


def make_response(seq_id, contents):
    return {'seq': seq_id, 'contents': contents}

class FakeBackend():
    """
    Fakes responses from the stack-ide process
    Override responses by passing in a dict keyed by tag
    """

    def __init__(self, responses={}):
        self.responses = responses
        if self.responses is None:
            raise Exception('stopthat!')

    def send_request(self, req):

        if self.handler:
            self.return_test_data(req)

    def return_test_data(self, req):

        tag = req.get('tag')
        seq_id = req.get('seq')

        # overrides
        if self.responses is None:
            raise Exception('wtf!')
        override = self.responses.get(tag)
        if override:
            self.handler(seq_response(seq_id, override))
            return

        # default responses
        if tag == 'RequestUpdateSession':
            return
        if tag == 'RequestShutdownSession':
            return
        if tag == 'RequestGetSourceErrors':
            self.handler(make_response(seq_id, []))
            return
        if tag == 'RequestGetExpTypes':
            self.handler(seq_response(seq_id, exp_types_response))
            return
        else:
            raise Exception(tag)
