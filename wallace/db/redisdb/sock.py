import redis

from wallace.config import register_connection


class RedisSocket(redis.Redis):

    @classmethod
    def construct(cls, name=None, **kwargs):
        socket = cls(**kwargs)
        if name:
            register_connection(name, socket)
        return socket
