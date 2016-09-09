from wallace.errors import SetupError, ValidationError


class ValidatorMixin(object):

    validators = ()

    def __init__(self, validators):
        self._check_all_validators(validators)
        self.validators = self._merge_validators(validators)

    def validate(self, val):
        for f in self.validators:
            if not f(val):
                raise ValidationError(305, val)

    @classmethod
    def _merge_validators(cls, validators):
        base_vals = cls.validators + ()  # workaround for tuple deepcopy
        if validators:
            return base_vals + tuple(validators)
        return base_vals

    @classmethod
    def _check_all_validators(cls, validators):
        cls._check_validators(cls.validators)
        if validators:
            cls._check_validators(validators)

    @staticmethod
    def _check_validators(validators):
        if not isinstance(validators, (list, tuple,)):
            raise SetupError(306, 'validators not iterable')
        for validator in validators:
            if not hasattr(validator, '__call__'):
                raise SetupError(307, 'validator not callable')
