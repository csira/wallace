from contextlib import contextmanager

from wallace.config import GetDBConn
from wallace.db.base import KeyValueModel


class Pipeline(object):

    @contextmanager
    def __get__(self, inst, owner):
        with owner.db.pipeline() as pipe:
            yield pipe


@contextmanager
def pipeline_execute(db, pipe=None):
    execute = False
    if pipe is None:
        pipe = db.pipeline()
        execute = True

    yield pipe

    if execute:
        pipe.execute()


class RedisHash(KeyValueModel):

    db = GetDBConn()
    db_name = None
    pipeline = Pipeline()

    def _read_data(self):
        return self.db.hgetall(self.db_key)

    def _write_data(self, state, _, pipe=None):
        with pipeline_execute(self.db, pipe) as pipeline:
            pipeline.delete(self.db_key)        # full refresh to clean
            pipeline.hmset(self.db_key, state)  # up deleted fields

    def delete(self):
        self.db.delete(self.db_key)


class ExpiringRedisHash(RedisHash):

    ttl = 10 * 60

    def _write_data(self, state, _, pipe=None):
        with pipeline_execute(self.db, pipe) as pipeline:
            super(ExpiringRedisHash, self)._write_data(state, _, pipe=pipeline)
            pipeline.expire(self.db_key, self.ttl)
