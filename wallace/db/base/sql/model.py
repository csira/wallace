from wallace.db.base.attrs.base import DataType
from wallace.db.base.model import Base, Model
from wallace.db.base.sql.table import SqlTable
from wallace.errors import DoesNotExist, SetupError, ValidationError


def get_primary_key_fields(bases, dct):
    pk_fields = set()

    for base in bases:  # support model inheritance
        for key in getattr(base, '_cbs_primary_key_fields', []):
            pk_fields.add(key)

    for key, val in dct.iteritems():
        if isinstance(val, DataType) and val.is_pk:
            pk_fields.add(key)
        elif key in pk_fields:      # catch any superclass pk fields
            pk_fields.remove(key)   # overridden here by a non-pk one

    return tuple(pk_fields)


class SqlModelBase(Base):

    def __new__(cls, name, bases, dct):
        dct['_cbs_primary_key_fields'] = get_primary_key_fields(bases, dct)
        return super(SqlModelBase, cls).__new__(cls, name, bases, dct)


class SqlModel(Model):

    __metaclass__ = SqlModelBase

    table = None

    def __init__(self):
        Model.__init__(self)

        if not self._cbs_primary_key_fields:
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

    @property
    def primary_key(self):
        # As CURRENTLY stored in the DB. If a PK field changes, this will
        # continue to return the old value so updates can find the row.
        return self._get_primary_key()

    def _get_primary_key(self):
        key = {}

        for attr in self._cbs_primary_key_fields:
            try:
                val = self._cbs_db_data[attr]
            except KeyError:
                raise ValidationError(404, 'null primary key field %s' % attr)

            if isinstance(val, basestring) and not val:
                raise ValidationError(404, 'empty primary key field %s' % attr)

            key[attr] = val

        return key

    @classmethod
    def find_one(cls, **kw):
        if not kw:
            raise ValidationError(407)
        row = cls.table.find_one(**kw)
        return cls.construct(new=False, **row)

    @classmethod
    def find_all(cls, **kwargs):
        rows = cls.table.select(**kwargs)
        return [cls.construct(new=False, **row) for row in rows]

    @classmethod
    def exists(cls, **kw):
        return cls.table.exists(**kw)
