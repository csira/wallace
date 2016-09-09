from wallace.config.cache import get_connection
from wallace.errors import ConfigError

# importing these below (circular reference)
# from wallace.db import MongoPool, PostgresPool, RedisSocket


def get_app():
    return App._inst


class Config(object):

    def __init__(self, **kw):
        self.config = kw


class App(object):

    _inst = None
    _config = None

    def __init__(self, **kw):
        App._inst = self
        App._config = Config(**kw)

    @property
    def config(self):
        return App._config.config


    def __getattr__(self, key):
        try:
            return self.config[key]
        except KeyError:
            raise ConfigError(101, 'param {} does not exist'.format(key))

    def __setattr__(self, key, val):
        self.config[key] = val

    def __delattr__(self, key):
        try:
            self.config.pop(key)
            return True
        except KeyError:
            return False


    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setitem__(self, key, val):
        self.__setattr__(key, val)

    def __delitem__(self, key):
        return self.__delattr__(key)


    @staticmethod
    def get_connection(name):
        return get_connection(name)

    @staticmethod
    def add_postgres_connection(
            database, host, port=5432,
            name='default_pg', **kw):

        from wallace.db import PostgresPool
        return PostgresPool.construct(
            name=name, database=database, host=host, port=port, **kw)

    @staticmethod
    def add_redis_connection(host, port=6379, name='default_redis', **kw):
        from wallace.db import RedisSocket
        return RedisSocket.construct(name=name, host=host, port=port, **kw)

    @staticmethod
    def add_mongo_connection(name='default_mongo', **kw):
        from wallace.db import MongoPool
        return MongoPool.construct(name=name, **kw)


    @staticmethod
    def get_db_conn(name):
        '''Deprecated.'''
        return get_connection(name)
