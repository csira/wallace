from wallace.config.app import get_app


class GetApp(object):

    def __get__(self, _, __):
        return get_app()


class GetDBConn(object):

    app = GetApp()

    def __init__(self, db_name=None):
        self.db_name = db_name

    def __get__(self, _, owner):
        db_name = self.db_name or owner.db_name
        return self.app.get_connection(db_name)


class GetParameter(object):

    app = GetApp()

    def __init__(self, attr):
        self._attr = attr

    def __get__(self, _, __):
        return self.app[self._attr]
