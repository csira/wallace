from tests.utils import should_throw
from tests.utils.registry import register

from wallace.db import DataType
from wallace.errors import ValidationError


@register
@should_throw(ValidationError, 301)
def test_missing_data_type():
    class MyType(DataType):
        pass


@register
@should_throw(ValidationError, 308)
def test_no_match():
    class MyType(DataType):
        data_type = str

    MyType._handle_typing([1,2,3])


@register
def test_castable():
    class MyType(DataType):
        data_type = int

        @staticmethod
        def cast_to_type(val):
            if isinstance(val, float):
                if int(val) == val:
                    return int(val)
            raise ValidationError(308)

    assert MyType._handle_typing(1.0) == 1


@register
@should_throw(ValidationError, 309)
def test_datatype_not_a_type():
    class MyType(DataType):
        data_type = 1


@register
def test_defaut_validates():
    class MyType(DataType):
        data_type = int
        default = 1


@register
@should_throw(ValidationError, 308)
def test_default_does_not_validate():
    class MyType(DataType):
        data_type = int
        default = 'abc'


@register
def test_callable_default():
    class MyType(DataType):
        data_type = int
        default = lambda: 1 + 2


@register
def test_default_ok_with_val():
    class MyType(DataType):
        data_type = int
        default = 1
        validators = (lambda val: val > 0,)


@register
@should_throw(ValidationError, 302)
def test_default_ok_with_val():
    class MyType(DataType):
        data_type = int
        default = 1
        validators = (lambda val: val > 1,)
