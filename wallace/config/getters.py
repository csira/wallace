from wallace.config.ns import get_app


class GetApp(object):
    def __get__(self, inst, owner):
        return get_app()


class GetDBConn(object):

    app = GetApp()

    def __get__(self, inst, owner):
        return self.app.get_db_conn(owner.db_name)


class GetParameter(object):

    app = GetApp()

    def __init__(self, attr):
        self._attr = attr

    def __get__(self, inst, owner):
        return self.app[self._attr]
