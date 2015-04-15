from contextlib import contextmanager

from wallace.config import GetDBConn
from wallace.db.base import KeyValueModel


class RedisHash(KeyValueModel):

    db = GetDBConn()
    db_name = None

    @contextmanager
    def _pipe_state_mgr(self, pipe=None):
        if pipe is None:
            pipe = self.db.pipeline()
            execute = True
        else:
            execute = False

        yield pipe

        if execute:
            pipe.execute()

    def _read_data(self):
        return self.db.hgetall(self.db_key)

    def _write_data(self, state, _, pipe=None):
        with self._pipe_state_mgr(pipe) as pipe:
            pipe.delete(self.db_key)        # delete first to
            pipe.hmset(self.db_key, state)  # clear deleted fields

    def delete(self, pipe=None):
        with self._pipe_state_mgr(pipe) as pipe:
            pipe.delete(self.db_key)


class ExpiringRedisHash(RedisHash):

    ttl = 10 * 60

    def _write_data(self, state, _, pipe=None):
        with self._pipe_state_mgr(pipe) as pipe:
            super(ExpiringRedisHash, self)._write_data(state, _, pipe=pipe)
            pipe.expire(self.db_key, self.ttl)
