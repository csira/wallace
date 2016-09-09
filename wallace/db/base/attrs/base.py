from wallace.db.base.attrs.interface import ModelInterface
from wallace.db.base.attrs.validator_mixin import ValidatorMixin
from wallace.errors import ValidationError, WallaceError


class _Base(type):

    def __new__(cls, name, bases, dct):
        default = dct.get('default')
        if callable(default):
            dct['default'] = staticmethod(default)

        return super(_Base, cls).__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(_Base, cls).__init__(name, bases, dct)

        if name == 'DataType':  # 'data_type' is not set on the base
            return

        if not cls.data_type:
            raise ValidationError(301, 'data_type cannot be None')

        if not isinstance(cls.data_type, type):
            raise ValidationError(309)

        cls._validate_default()

    def _validate_default(cls):
        default = cls.default() if callable(cls.default) else cls.default
        if default is None:
            return

        cls._handle_typing(default)

        for func in cls.validators:
            if not func(default):
                msg = 'default "{}" does not validate'.format(default)
                raise ValidationError(302, msg)


class DataType(ModelInterface, ValidatorMixin):

    __metaclass__ = _Base

    data_type = None

    def __init__(self, validators=None, default=None, pk=False, key=False):
        if self.__class__.__name__ == 'DataType':
            raise WallaceError(303, "DataType cannot be used directly")

        ValidatorMixin.__init__(self, validators)
        ModelInterface.__init__(self, pk=pk, key=key, default=default)

        if self.default is not None:  # validation only, the model instance doesn't exist yet
            val = self.default() if callable(self.default) else self.default
            if val is not None:
                val = self._handle_typing(val)
                self.validate(val)

    def __set__(self, inst, val):
        if val is None:
            self.__delete__(inst)
            return

        if inst.middleware:
            val = inst.middleware.cast(self.data_type, val)

        val = self._handle_typing(val)

        self.validate(val)
        super(DataType, self).__set__(inst, val)

    @classmethod
    def _handle_typing(cls, val):
        if isinstance(val, cls.data_type):
            return val

        val = cls.cast_to_type(val)

        if not isinstance(val, cls.data_type):
            raise ValidationError(304)

        return val

    @staticmethod
    def cast_to_type(val):
        raise ValidationError(308)
