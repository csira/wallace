from wallace.db.base.attrs.base import DataType
from wallace.db.base.model import Base, Model
from wallace.errors import DoesNotExist, SetupError, ValidationError


class NoSqlBase(Base):

    def __new__(cls, name, bases, dct):
        is_found = cls._find_key_field_or_property(dct)
        if not is_found:
            is_found = cls._find_parameter(dct)
        if not is_found:
            cls._comb_superclasses(bases, dct)

        return super(NoSqlBase, cls).__new__(cls, name, bases, dct)

    @staticmethod
    def _find_key_field_or_property(dct):
        key = dct.get('key')
        if not key:
            return False

        if not isinstance(key, property) and not isinstance(key, DataType):
            raise SetupError(503)

        return True

    @classmethod
    def _find_parameter(cls, dct):
        '''Search for the 'key=True' case, and confirm no more than one parameter has that property.'''

        num_found = 0
        field = None

        for key, val in dct.iteritems():
            if isinstance(val, DataType) and val.is_key:
                field = key
                num_found += 1

        if num_found > 1:
            raise SetupError(502)
        elif num_found == 0:
            return False

        dct['_cbs_key_field'] = field
        dct['key'] = cls._build_prop(field)
        return True

    @classmethod
    def _comb_superclasses(cls, bases, dct):
        for base in bases:
            if hasattr(base, 'key'):
                break  # will inherit naturally

            field = getattr(base, '_cbs_key_field', '')
            if field:
                dct['_cbs_key_field'] = field
                dct['key'] = cls._build_prop(field)
                break

    @staticmethod
    def _build_prop(field):
        return property(lambda self: getattr(self, field))


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
