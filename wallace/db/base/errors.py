from wallace.errors import Error


class DBError(Error):
    pass


class DoesNotExist(DBError):
    pass


class ValidationError(DBError):
    pass
