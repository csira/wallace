from wallace.db.base.attrs.base import DataType
from wallace.db.base.model import Base
from wallace.errors import ValidationError


class SqlModelBase(Base):

    def __new__(cls, name, bases, dct):
        fields = dct["_pk_fields"] = get_primary_key_fields(bases, dct)
        dct["primary_key"] = PrimaryKey(fields)
        return super(SqlModelBase, cls).__new__(cls, name, bases, dct)


class PrimaryKey(object):
    """
    The primary key as it is currently stored in the db. When a PK field changes,
    this continues to return the old value so the row can be found.

    Note if this is a new model, this will return an empty PK since the row
    doesn't yet exist.

    """
    def __init__(self, fields):
        self.fields = fields

    def __get__(self, inst, _):
        key = dict()

        for attr in self.fields:
            try:
                val = inst._state.db_state[attr]
            except KeyError:
                raise ValidationError(404, "null primary key field {}".format(attr))

            if isinstance(val, basestring) and not val:
                raise ValidationError(404, "empty primary key field {}".format(attr))

            key[attr] = val

        return key


def get_primary_key_fields(bases, dct):
    pk_fields = set()

    for base in bases:  # support model inheritance
        for key in getattr(base, "_pk_fields", []):
            pk_fields.add(key)

    for key, val in dct.iteritems():
        if isinstance(val, DataType) and val.is_pk:
            pk_fields.add(key)
        elif key in pk_fields:      # catch any superclass pk fields
            pk_fields.remove(key)   # overridden here by a non-pk one

    return tuple(pk_fields)
