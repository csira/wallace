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

    validators = ()

    @staticmethod
    def _check_validators(validators):
        if not isinstance(validators, (list, tuple,)):
            raise TypeError('validators not iterable')
        for validator in validators:
            if not hasattr(validator, '__call__'):
                raise TypeError('validator not callable')

    @classmethod
    def _check_all_validators(cls, validators):
        cls._check_validators(cls.validators)
        if validators:
            cls._check_validators(validators)

    @classmethod
    def _merge_validators(cls, validators):
        base_vals = cls.validators + ()  # workaround for tuple deepcopy
        if validators:
            return base_vals + tuple(validators)
        return base_vals

    def __init__(self, validators):
        self._check_all_validators(validators)
        self.validators = self._merge_validators(validators)

    def validate(self, val):
        for f in self.validators:
            if not f(val):
                raise ValidationError(val)


class _TypecastMixin(object):

    cast = None

    @classmethod
    def typecast(cls, val):
        try:
            return cls.cast(val) if cls.cast else val
        except ValueError:
            raise ValidationError(val)


def _check_default_validates(default, cast_func, validators):
    if default is None:
        return

    if callable(default):
        default = default()

    if cast_func:
        if not isinstance(default, cast_func):
            msg = 'default `%s` not a %s' % (default, cast_func.__name__,)
            raise ValidationError(msg)

    for func in validators:
        if not func(default):
            msg = 'default `%s` does not validate' % default
            raise ValidationError(msg)


class _Base(type):
    def __new__(cls, name, bases, dct):
        default = dct.get('default')
        if default and callable(default):
            dct['default'] = staticmethod(default)

        validators = dct.get('validators', ())
        if validators:
            dct['validators'] = cls._merge_base_validators(bases, validators)

        return super(_Base, cls).__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(_Base, cls).__init__(name, bases, dct)
        _check_default_validates(cls.default, cls.cast, cls.validators)

    @staticmethod
    def _merge_base_validators(bases, validators):
        all_validators = []
        for base in bases:
            for val in getattr(base, 'validators', ()):
                all_validators.append(val)

        for val in validators:
            all_validators.append(val)

        return tuple(all_validators)


class DataType(_Interface, _ValidationMixin, _TypecastMixin):

    __metaclass__ = _Base

    def __init__(self, validators=None, **kwargs):
        _Interface.__init__(self, **kwargs)
        _ValidationMixin.__init__(self, validators)
        _TypecastMixin.__init__(self)

        _check_default_validates(self.default, self.cast, self.validators)

    def __set__(self, inst, val):
        if val is None:
            self.__delete__(inst)
            return

        val = self.typecast(val)
        self.validate(val)
        super(DataType, self).__set__(inst, val)
