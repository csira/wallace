from wallace.config import GetDBConn
from wallace.errors import DoesNotExist


class _Database(object):

    def __get__(self, inst, owner):
        return owner.db[owner.database_name]


class _Collection(object):

    def __get__(self, inst, owner):
        return owner.database[owner.collection_name]


class MongoCollection(object):

    db = GetDBConn()
    db_name = None

    database = _Database()
    database_name = None

    collection = _Collection()
    collection_name = None

    @classmethod
    def fetchone(cls, **kwargs):
        return cls.collection.find_one(spec_or_id=kwargs)

    @classmethod
    def fetchall(cls, **kwargs):
        data = cls.collection.find(kwargs)
        return list(data)

    @classmethod
    def add(cls, **data):
        cls.collection.insert(data)

    @classmethod
    def update(cls, **data):
        cls.collection.save(data)

    @classmethod
    def delete(cls, key):
        if not key:             # `remove` drops all documents in the
            raise DoesNotExist  # collection if `spec_or_id` is None
        cls.collection.remove(spec_or_id=key, multi=False)
