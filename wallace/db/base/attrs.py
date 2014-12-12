import time

from wallace.db.base.errors import ValidationError


class _Interface(object):

    default = None

    def __init__(self, pk=False, default=None):
        self.attr = None
        self.is_pk = pk
        if default is not None:
            self.default = default

    def __get__(self, inst, owner):
        return inst._get_attr(self.attr)

    def __set__(self, inst, val):
        inst._set_attr(self.attr, val)

    def __delete__(self, inst):
        inst._del_attr(self.attr)


class _ValidationMixin(object):

    @staticmethod
    def _check_validators(validators):
        if not isinstance(validators, (list, tuple,)):
            raise TypeError('validators not iterable')
        for validator in validators:
            if not hasattr(validator, '__call__'):
                raise TypeError('validator not callable')

    def __init__(self, validators):
        if validators:
            self._check_validators(validators)
            self._validators = tuple(validators)
        else:
            self._validators = ()

    def validate(self, val):
        for f in self._validators:
            if not f(val):
                raise ValidationError(val)


class _TypecastMixin(object):

    cast = None

    @classmethod
    def typecast(cls, val):
        return cls.cast(val) if cls.cast else val

    @classmethod
    def check_type(cls, val):
        if not isinstance(val, cls.cast):
            raise ValidationError(val)


class DataType(_Interface, _ValidationMixin, _TypecastMixin):
    def __init__(self, validators=None, **kwargs):
        _Interface.__init__(self, **kwargs)
        _ValidationMixin.__init__(self, validators)
        _TypecastMixin.__init__(self)

    def __get__(self, inst, owner):
        val = super(DataType, self).__get__(inst, owner)
        if val is None:
            return val
        return self.typecast(val)

    def __set__(self, inst, val):
        if val is None:
            self.__delete__(inst)
            return

        self.check_type(val)
        self.validate(val)
        super(DataType, self).__set__(inst, val)




class Boolean(DataType):

    cast = bool
    default = False

    @classmethod
    def typecast(cls, val):
        if isinstance(val, basestring):
            return val == 'True' or val == 'true'
        return super(Boolean, cls).typecast(val)


class ByteArray(DataType):

    cast = bytearray


class Float(DataType):

    cast = float
    default = 0.0


class Integer(DataType):

    cast = int
    default = 0


class Moment(Integer):

    default = None


class Now(Moment):

    default = time.time


class String(DataType):

    cast = str


class Unicode(DataType):

    cast = unicode
