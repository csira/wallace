import ujson

from wallace.config.app import App, get_app
from wallace.config.cache import get_connection, register_connection
from wallace.config.getters import GetApp, GetDBConn, GetParameter
from wallace.errors import ConfigError


def setup_app(config):
    '''Deprecated.'''

    if isinstance(config, str):
        data = _deserialize(config)
    elif isinstance(config, dict):
        data = config
    else:
        raise ConfigError('must provide a filename or dictionary')

    db_conn_data = data.pop('db', None)
    app = App(**data)

    if not db_conn_data:
        return app

    for name, conn_data in db_conn_data.iteritems():
        db = conn_data['db']
        conn_cls = _get_conn(db)
        conn_cls.construct(name=name, **conn_data)

    return app


def _deserialize(filename):
    with open(filename, 'r') as f:
        data = f.read()
        return ujson.loads(data)


def _get_conn(db):
    from wallace.db import MongoPool, PostgresPool, RedisSocket
    if db == 'mongo':
        return MongoPool
    if db == 'postgres':
        return PostgresPool
    if db == 'redis':
        return RedisSocket
    raise ConfigError('unknown db "%s" % db')


__all__ = [
    'get_connection', 'register_connection',
    'GetApp', 'GetDBConn', 'GetParameter',
    'App', 'get_app',
    'setup_app',
]
