from wallace.db.base.attrs.base import DataType
from wallace.db.base.model import Base, Model
from wallace.errors import DoesNotExist, SetupError, ValidationError


class NoSqlBase(Base):

    def __new__(cls, name, bases, dct):
        key = dct.get('key')

        if key:
            if not isinstance(key, property) and not isinstance(key, DataType):
                raise SetupError(503)
        else:
            field = None

            for key, val in dct.iteritems():
                if isinstance(val, DataType) and val.is_key:
                    if field:
                        raise SetupError(502)
                    field = key

            if field:
                dct['_cbs_key_field'] = field
                key = dct['key'] = property(lambda self: getattr(self, field))

        if not key:  # comb superclasses
            for base in bases:
                has_key = hasattr(base, 'key')
                if has_key:  # will inherit naturally
                    break

                field = base.get('_cbs_key_field')
                if field:
                    dct['_cbs_key_field'] = field
                    key = dct['key'] = property(lambda self: getattr(self, field))
                    break

        return super(NoSqlBase, cls).__new__(cls, name, bases, dct)


class NoSqlModel(Model):
    '''Base model for NoSql-like, key/value db's.

    Stored by the value at 'inst.key'. Configure in one of these ways:

    Wallace type 1:

        class MyModel(RedisHash):
            key = String()
            first_name = String()
            last_name = String()


    Wallace type 2:

        class MyModel(RedisHash):
            first_name = String(key=True)
            last_name = String()

        NB: in this case 'key=True' must be specified for exactly one field


    Property:

        class MyModel(RedisHash):
            first_name = String()
            last_name = String()

            @property
            def key(self):
                return "{}|{}".format(self.first_name, self.last_name)

    NB: This model is not currently appropriate for implementing records stored
    with a composite key. While it's possible to make composite-like keys by
    creating a property that uses 2+ fields (a la example above), the
    key property still returns only a single value.

    '''

    __metaclass__ = NoSqlBase

    def __init__(self):
        Model.__init__(self)

        if not hasattr(self, 'key'):
            raise SetupError(501)

    def pull(self, *a, **kw):
        if not self.key:
            raise ValidationError(501)
        return super(NoSqlModel, self).pull(*a, **kw)

    def push(self, *a, **kw):
        if not self.key:
            raise ValidationError(501)
        return super(NoSqlModel, self).push(*a, **kw)

    def delete(self):
        if not self.key:
            raise DoesNotExist(202, 'new model')
        super(NoSqlModel, self).delete()
