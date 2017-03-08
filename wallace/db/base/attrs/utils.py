from wallace.errors import SetupError, ValidationError


def validate_default(default, data_type, nullable, validators):
    val = default() if callable(default) else default

    if val is None:
        if nullable:
            return
        raise ValidationError(313, 'default cannot be null')

    if not isinstance(val, data_type):
        raise TypeError('"{}" must be a {}'.format(val, data_type))

    validate(val, *validators)


def check_validators(validators):
    if not isinstance(validators, (list, tuple,)):
        raise SetupError(306, 'validators not iterable')
    for validator in validators:
        if not hasattr(validator, '__call__'):
            raise SetupError(307, 'validator not callable')


def validate(val, *validators):
    for func in validators:
        if not func(val):
            raise ValidationError(302, '"{}" does not validate'.format(val))
