import functools
import uuid

from tests.utils import should_throw
from tests.utils.registry import register

from wallace.db import Model, String, NoSqlModel
from wallace.errors import DoesNotExist


def _insert_model(f):
    @functools.wraps(f)
    def wraps():
        class MyDriver(NoSqlModel):
            pass

        class MyModel(MyDriver):
            key = String()

        return f(MyModel)
    return wraps


@register
@_insert_model
@should_throw(DoesNotExist, 202)
def test_delete_without_key(model):
    obj = model.new()
    obj.delete()
