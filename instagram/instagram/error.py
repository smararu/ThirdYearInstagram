class PrivateAccountError(Exception):
    pass


class UnexpectedResult(Exception):
    pass


class HTTPRetreivalError(Exception):
    def __init__(self, code=None):
        if code:
            self.code = code
