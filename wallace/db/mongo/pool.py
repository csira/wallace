import pymongo

from wallace.config import register_connection


class MongoPool(pymongo.MongoClient):

    @classmethod
    def construct(cls, name=None, **kwargs):
        pool = cls(**kwargs)
        if name:
            register_connection(name, pool)
        return pool
