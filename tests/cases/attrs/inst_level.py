from tests.utils import should_throw
from tests.utils.registry import register

from wallace.db import DataType
from wallace.db import Model, String
from wallace.errors import ValidationError, WallaceError


@register
@should_throw(WallaceError, 303)
def test_instantiate_base_type():
    DataType()


@register
def test_instantiate_subclass():
    class MyType(DataType):
        data_type = int

    MyType()


@register
def test_set_none_is_delete():
    class TestModel(Model):
        my_val = String()

    test = TestModel.construct(my_val='abc')
    assert test.my_val == 'abc'
    assert test._state.db_state == {'my_val': 'abc'}
    assert test._state.deleted_attrs == set()

    test.my_val = None
    assert test.my_val is None
    assert test._state.db_state == {'my_val': 'abc'}
    assert test._state.deleted_attrs == set(['my_val'])


@register
@should_throw(ValidationError, 302)
def test_set_value_if_validator_fails():
    class TestModel(Model):
        my_val = String(validators=(lambda val: len(val) < 4,))

    test = TestModel.construct(my_val='abc')
    test.my_val = 'abcd'


# @register
# # @should_throw(ValidationError, 204)
# def test_save_if_not_nullable():
#     class MyModel(Model):
#         my_val = String(nullable=False)

#     test = MyModel.construct()
#     test.push()



@register
def test_validator_merge():
    f1 = lambda val: val.startswith('a')
    f2 = lambda val: val.endswith('z')
    f3 = lambda val: len(val) < 4

    class MyType(DataType):
        data_type = str
        default = 'az'
        validators = (f1, f2)

    test = MyType(validators=(f3,))

    assert len(test.validators) == 3
    assert f1 in test.validators
    assert f2 in test.validators
    assert f3 in test.validators


@register
@should_throw(ValidationError, 302)
def test_default_fails_1():
    class MyType(DataType):
        data_type = int
        validators = (lambda val: val > 10,)

    MyType(default=5)


@register
@should_throw(ValidationError, 302)
def test_default_fails_2():
    class MyType(DataType):
        data_type = int
        validators = (lambda val: val > 10,)

    MyType(default=15, validators=(lambda val: val < 14,))


@register
@should_throw(ValidationError, 302)
def test_default_fails_3():
    class MyType(DataType):
        data_type = int
        default = 10

    MyType(validators=(lambda val: val < 10,))
