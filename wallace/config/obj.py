import ujson

from wallace.config.cache import get_connection, register_connection
from wallace.config.errors import ConfigError

# some addl imports in ``_spin_up``


def _spin_up(db, **kw):
    if db == 'mongo':
        from wallace.db import MongoPool
        return MongoPool.construct(**kw)
    if db == 'postgres':
        from wallace.db import PostgresPool
        return PostgresPool.construct(**kw)
    if db == 'redis':
        from wallace.db import RedisSocket
        return RedisSocket.construct(**kw)
    raise ConfigError('unknown db "%s"' % db)


class App(object):
    def __init__(self, **kwargs):
        self._config = kwargs

    @property
    def config(self):
        return self._config

    def __getitem__(self, key):
        try:
            return self._config[key]
        except KeyError:
            raise ConfigError('config param "%s" not provided' % key)

    def _get_db_parameters(self, name):
        try:
            return self['db'][name]
        except KeyError:
            raise ConfigError('db params for "%s" not provided ' % name)

    def get_db_conn(self, name):
        db = get_connection(name, silent=True)
        if not db:
            data = self._get_db_parameters(name)
            db = _spin_up(**data)
            register_connection(name, db)
        return db
