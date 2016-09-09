from contextlib import contextmanager

from wallace.config import GetDBConn
from wallace.db.base.nosql.model import NoSqlModel
from wallace.db.redisdb.middleware import RedisMiddleware


class RedisHash(NoSqlModel):

    db = GetDBConn()
    db_name = None

    middleware = RedisMiddleware()

    @classmethod
    def exists(cls, **kw):
        inst = cls.construct(**kw)
        return cls.db.exists(inst.key)

    def read_from_db(self):
        return self.db.hgetall(self.key)

    def write_to_db(self, state, _, pipe=None):
        with self._db_conn_manager(pipe) as pipe:
            pipe.delete(self.key)        # delete first to clear deleted
            pipe.hmset(self.key, state)  # fields and clean up orphans

    def delete(self, pipe=None):
        super(RedisHash, self).delete()

        with self._db_conn_manager(pipe) as pipe:
            pipe.delete(self.key)

    @contextmanager
    def _db_conn_manager(self, pipe=None):
        if pipe is None:
            pipe = self.db.pipeline()
            execute = True
        else:
            execute = False

        yield pipe

        if execute:
            pipe.execute()
