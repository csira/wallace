from wallace.db.redisdb.hash import RedisHash
from wallace.errors import ConfigError


class ExpiringRedisHash(RedisHash):

    ttl = None  # must explicitly set ttl

    def __init__(self, *a, **kw):
        RedisHash.__init__(self, *a, **kw)

        if not isinstance(self.ttl, int) or self.ttl < 1:
            raise ConfigError(801, 'int ttl >=1 required')

    def write_to_db(self, state, _, pipe=None):
        with self._pipe_manager(pipe) as pipe:
            super(ExpiringRedisHash, self).write_to_db(state, _, pipe=pipe)
            pipe.expire(self.key, self.ttl)
