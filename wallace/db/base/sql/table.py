import functools

from wallace.config import GetDBConn
from wallace.db.base.sql.writer import QueryWriter
from wallace.errors import DoesNotExist, SetupError, ValidationError


def catch_missing_table_name(f):
    @functools.wraps(f)
    def wrapper(cls, *a, **kw):
        if not cls.table_name:
            raise SetupError(405, 'must set table_name')

        if not cls._query_writer:
            cls._query_writer = QueryWriter(cls.table_name)

        return f(cls, *a, **kw)
    return wrapper


class SqlTable(object):

    db = GetDBConn()
    db_name = None
    table_name = None

    _query_writer = None

    @classmethod
    @catch_missing_table_name
    def delete(cls, **kw):
        q, vals = cls._query_writer.delete(**kw)
        cls.db.execute(q, vals)

    @classmethod
    @catch_missing_table_name
    def exists(cls, **kw):
        q, vals = cls._query_writer.exists(**kw)
        data = cls.db.fetchone(q, vals)
        return data.get('exists')

    @classmethod
    @catch_missing_table_name
    def fetch_one(cls, **kw):
        q, vals = cls._query_writer.select(**kw)
        return cls.db.fetchone(q, vals)

    @classmethod
    @catch_missing_table_name
    def find_one(cls, **kw):
        if not kw:
            raise ValidationError(407)

        data = cls.select(limit=2, **kw)
        if not data:
            raise DoesNotExist(406)
        if len(data) != 1:
            raise ValidationError(407, 'expected a unique result')
        return data[0]

    @classmethod
    @catch_missing_table_name
    def insert(cls, **kw):
        q, vals = cls._query_writer.insert(**kw)
        cls.db.execute(q, vals)

    @classmethod
    @catch_missing_table_name
    def select(cls, **kw):
        q, vals = cls._query_writer.select(**kw)
        return cls.db.fetchall(q, vals)

    @classmethod
    @catch_missing_table_name
    def update(cls, new_data, **kw):
        q, vals = cls._query_writer.update(new_data, **kw)
        cls.db.execute(q, vals)


    @classmethod
    @catch_missing_table_name
    def _for_testing_only(cls):
        pass
