from tests.utils import should_throw
from tests.utils.registry import register

from wallace.db import Model, String


@register
def attrs_other_1():
    class MyModel(Model):
        attr = String(nullable=True, default=None, validators=(lambda val: val in ["a", "b"],))

    inst = MyModel.construct()
