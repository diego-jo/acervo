class NotFound(Exception):
    def __init__(self, msg):
        self.msg = msg


class DuplicatedRegistry(Exception):
    def __init__(self, msg):
        self.msg = msg


class ForbidenOperation(Exception):
    def __init__(self, msg):
        self.msg = msg


class InternalError(Exception):
    def __init__(self, msg):
        self.msg = msg
