from wallace.db.base.model import Model
from wallace.db.base.sql.meta import SqlModelBase
from wallace.db.base.sql.table import SqlTable
from wallace.errors import DoesNotExist, SetupError, ValidationError


class SqlModel(Model):

    __metaclass__ = SqlModelBase

    table = None
    primary_key = None  # set up by the base

    def __init__(self, *a, **kw):
        Model.__init__(self, *a, **kw)

        if not self._pk_fields:
            raise SetupError(401, 'no primary key fields defined')
        if not self.table:
            raise SetupError(402, 'not tied to a table')
        if not issubclass(self.table, SqlTable):
            raise SetupError(403, 'table does not subclass SqlTable')

    def read_from_db(self):
        return self.table.fetch_one(**self.primary_key)

    def write_to_db(self, state, changes):
        if self.is_new:
            self.table.insert(**state)
        else:
            self.table.update(changes, **self.primary_key)

    def delete(self):
        super(SqlModel, self).delete()
        self.table.delete(**self.primary_key)

    @classmethod
    def find_one(cls, **kw):
        if not kw:
            raise ValidationError(407)
        row = cls.table.find_one(**kw)
        return cls.construct(**row)

    @classmethod
    def find_all(cls, **kw):
        rows = cls.table.select(**kw)
        return [cls.construct(**row) for row in rows]

    @classmethod
    def exists(cls, **kw):
        return cls.table.exists(**kw)
