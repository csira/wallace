import functools

from tests.utils.registry import register

from wallace.db import Model, String


def _insert_model(f):
    @functools.wraps(f)
    def wraps():
        class TestModel(Model):
            a = String()
            b = String(default='default')
        return f(TestModel)
    return wraps


@register
@_insert_model
def test_default_discovery(model):
    assert model._cbs_default_fields == (('a', ''), ('b', 'default'),)


@register
@_insert_model
def test_new(model):
    inst = model.new()
    assert inst.raw == {'a': '', 'b': 'default'}


@register
@_insert_model
def test_construct_1(model):
    inst = model.construct(new=True, a='abc')
    assert inst._cbs_updated == {'a': 'abc', 'b': 'default'}


@register
@_insert_model
def test_construct_2(model):
    inst = model.construct(new=False, a='abc')
    assert inst._cbs_db_data == {'a': 'abc'}


@register
def test_inheritance_default_1():
    class TestModel(Model):
        a = String()
        b = String(default='default')

    class Sub(TestModel):
        c = String(default='foo')

    fields = sorted(Sub._cbs_default_fields)
    assert fields == [('a', ''), ('b', 'default'), ('c', 'foo')]


@register
def test_inheritance_default_2():
    class TestModel(Model):
        a = String()
        b = String(default='default')

    class Sub(TestModel):
        b = String()
        c = String(default='foo')

    fields = sorted(Sub._cbs_default_fields)
    assert fields == [('a', ''), ('b', ''), ('c', 'foo')]
