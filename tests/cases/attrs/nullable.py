from tests.utils import should_throw
from tests.utils.registry import register

from wallace.db import Model, String
from wallace.errors import ValidationError


@register
@should_throw(ValidationError, 313)
def test_default_null_not_nullable():
    class MyType(String):
        default = None
        nullable = False


@register
@should_throw(ValidationError, 312)
def test_delete_not_nullable():
    class MyType(String):
        nullable = False

    class MyModel(Model):
        attr = MyType()

    inst = MyModel.construct(attr="abc")
    del inst.attr
