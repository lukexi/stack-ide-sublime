class FakeBackend():

    def __init__(self, response={}):
        self.response = response
        self.handler = None

    def send_request(self, req):
        self.response["seq"] = req.get("seq")
        if not self.handler is None:
            self.handler(self.response)
