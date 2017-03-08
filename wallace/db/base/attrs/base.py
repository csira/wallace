from wallace.db.base.attrs.interface import ModelInterface
from wallace.db.base.attrs.utils import validate_default, check_validators, validate
from wallace.errors import ValidationError, WallaceError

empty_sentinel = object()


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

        if not isinstance(cls.nullable, bool):
            raise ValidationError(310)

        check_validators(cls.validators)
        validate_default(cls.default, cls.data_type, cls.nullable, cls.validators)


class DataType(ModelInterface):

    __metaclass__ = _Base

    data_type = None
    default = None
    nullable = True
    validators = ()

    def __init__(self, pk=False, key=False, validators=empty_sentinel,
            default=empty_sentinel, nullable=empty_sentinel):

        if self.__class__.__name__ == 'DataType':
            raise WallaceError(303, "DataType cannot be used directly")

        self.validators = self._get_validators(validators)
        self.nullable = self._get_nullable_flag(nullable)
        default = self._get_default(default, self.nullable, self.validators)

        ModelInterface.__init__(self, pk=pk, key=key, default=default)

    @classmethod
    def _get_validators(cls, validators):
        if validators == empty_sentinel:
            return cls.validators

        check_validators(validators)

        if validators:
            cls_level = cls.validators + ()  # work-around for tuple deep-copy
            return cls_level + tuple(validators)

        return cls.validators

    @classmethod
    def _get_nullable_flag(cls, nullable):
        if nullable == empty_sentinel:
            return cls.nullable

        if not isinstance(nullable, bool):
            raise ValidationError(311)

        return nullable

    @classmethod
    def _get_default(cls, default, nullable, validators):
        if default == empty_sentinel:
            default = cls.default

        if default is None and not nullable:
            raise ValidationError(313)

        validate_default(default, cls.data_type, nullable, validators)
        return default


    def __get__(self, inst, owner):
        val = super(DataType, self).__get__(inst, owner)
        return self.after_get(val)

    @staticmethod
    def after_get(val):
        return val


    def __set__(self, inst, val):
        if val is None:
            self.__delete__(inst)
            return

        if inst.middleware:
            val = inst.middleware.cast(self.data_type, val)

        try:
            val = self.before_set(val)
        except ValueError as err:
            raise ValidationError(304, err.message)
        except TypeError as err:
            raise ValidationError(304, err.message)

        if not isinstance(val, self.data_type):
            raise ValidationError(304)

        validate(val, *self.validators)
        super(DataType, self).__set__(inst, val)

    @staticmethod
    def before_set(val):
        return val


    def __delete__(self, inst):
        if not self.nullable:
            raise ValidationError(312)
        super(DataType, self).__delete__(inst)


    @classmethod
    def _for_testing_inbound(cls, val):
        if val is None:
            if self.nullable:
                return
            raise ValidationError(312)

        try:
            val = cls.before_set(val)
        except ValueError as err:
            raise ValidationError(304, err.message)
        except TypeError as err:
            raise ValidationError(304, err.message)

        if not isinstance(val, cls.data_type):
            raise ValidationError(304)
