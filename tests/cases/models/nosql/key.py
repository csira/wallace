import functools

from tests.utils import should_throw
from tests.utils.registry import register

from wallace.db import String, NoSqlModel
from wallace.errors import SetupError


def _insert(f):
    @functools.wraps(f)
    def wraps():
        class Driver(NoSqlModel):
            pass
        return f(Driver)
    return wraps


@register
@_insert
@should_throw(SetupError, 501)
def check_no_key_field(Driver):
    class MyModel(Driver):
        name = String()

    inst = MyModel.construct(name='abc')


@register
@_insert
def check_key_named_field(Driver):
    class MyModel(Driver):
        key = String()
        name = String()

    inst = MyModel.construct(key='abc', name='xyz')
    assert inst.key == 'abc'


@register
@_insert
def check_key_flagged_field(Driver):
    class MyModel(Driver):
        foo = String(key=True)
        name = String()

    inst = MyModel.construct(foo='abc', name='xyz')
    assert inst.key == 'abc'


@register
@_insert
def check_key_in_both(Driver):
    class MyModel(Driver):
        key = String(key=True)
        name = String()

    inst = MyModel.construct(key='abc', name='xyz')
    assert inst.key == 'abc'


@register
@_insert
def check_key_prop(Driver):
    class MyModel(Driver):
        foo = String()
        name = String()
        @property
        def key(self):
            return self.name

    inst = MyModel.construct(foo='abc', name='xyz')
    assert inst.key == 'xyz'


@register
@_insert
@should_throw(AttributeError)
def check_key_named_and_prop(Driver):
    class MyModel(Driver):
        key = String()
        name = String()
        @property
        def key(self):
            return self.name

    inst = MyModel.construct(key='abc', name='def')


@register
@_insert
def check_key_flagged_and_prop(Driver):
    class MyModel(Driver):
        foo = String(key=True)
        name = String()
        @property
        def key(self):
            return self.name

    inst = MyModel.construct(foo='abc', name='xyz')
    assert inst.key == 'xyz'


@register
@_insert
@should_throw(AttributeError)
def check_all_three(Driver):
    class MyModel(Driver):
        key = String(key=True)
        name = String()
        @property
        def key(self):
            return self.name

    inst = MyModel.construct(key='abc', name='xyz')
