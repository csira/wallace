import redis
import ujson

from wallace.config.errors import ConfigError

# some addl imports in ``_spin_up``


def _spin_up(db, **kw):
    if db == 'postgres':
        from wallace.db import PostgresPool
        return PostgresPool.construct(kw.get('minconns', 1),
                                      kw.get('maxconns', 1),
                                      **kw)
    if db == 'redis':
        return redis.Redis(host=kw['host'], port=kw['port'])
    raise ConfigError('unknown db "%s"' % db)


class App(object):

    _db_conn_cache = {}

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

    def get_db_conn(self, name):
        db = self._db_conn_cache.get(name)
        if not db:
            data = self['db'][name]
            db = _spin_up(**data)
            self._db_conn_cache[name] = db
        return db
