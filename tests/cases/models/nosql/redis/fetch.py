import functools
import uuid

from tests.cases.models.nosql.redis._setup import set_up_and_tear_down, DB_NAME
from tests.utils import should_throw
from tests.utils.registry import register

from wallace.config import App
from wallace.db import String, Integer, RedisHash
from wallace.errors import DoesNotExist, ValidationError


def _make_model_without_key():
    class TestModel(RedisHash):
        db_name = DB_NAME
        key = String()
        test_int = Integer()
        test_str = String()
    inst = TestModel.construct(key='key', test_int=123, test_str='abc')
    inst.push()
    return TestModel, inst.key


def _make_model_with_key():
    class TestModel(RedisHash):
        db_name = DB_NAME
        test_int = Integer()
        test_str = String()

        @property
        def key(self):
            return '{}|{}'.format(self.test_str, str(self.test_int))

    inst = TestModel.construct(test_int=123, test_str='abc')
    inst.push()
    return TestModel, inst.key


# @register
@set_up_and_tear_down
def fetch_with_key_without_property():
    model, key = _make_model_without_key()
    inst = model.fetch(key=key)

    assert inst.raw['test_int'] == 123
    assert inst.raw['test_str'] == 'abc'


@register
@set_up_and_tear_down
def fetch_with_key_with_property():
    model, key = _make_model_with_key()
    inst = model.fetch(test_int=123, test_str='abc')
    assert key == inst.key == 'abc|123'


@register
@should_throw(ValidationError, 501)
@set_up_and_tear_down
def fetch_without_key_without_property():
    model, _ = _make_model_without_key()
    model.fetch(test_int=123, test_str='abc')


@register
@set_up_and_tear_down
def fetch_without_key_with_property():
    model, key = _make_model_with_key()
    inst = model.construct(test_int=123, test_str='abc')
    key = inst.key
    inst.pull()
    assert key == inst.key == 'abc|123'
