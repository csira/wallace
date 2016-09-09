class Error(Exception):
    def __init__(self, code=None, msg=None):
        self.code = code
        self.msg = msg


WallaceError = Error


class SetupError(Error):
    pass


class ConfigError(Error):
    pass


class DBError(Error):
    pass


class DoesNotExist(DBError):
    pass


class ValidationError(DBError):
    pass
