import time

from wallace import ExpiringRedisHash, String, Integer
from wallace.errors import ConfigError, DoesNotExist

from tests.cases.models.nosql.redis._setup import set_up_and_tear_down, DB_NAME
from tests.utils import should_throw
from tests.utils.registry import register, solo


class Foo(ExpiringRedisHash):
    db_name = DB_NAME
    ttl = 1  # second

    key = Integer()
    first_name = String()
    last_name = String()


@register
@should_throw(DoesNotExist, 203)
@set_up_and_tear_down
def test_expires_on_time():
    inst = Foo.construct(key=1, first_name='first', last_name='last')
    inst.push()

    time.sleep(0.9)
    Foo.fetch(key=1)
    time.sleep(0.1)
    Foo.fetch(key=1)


@register
@should_throw(ConfigError, 801)
def fails_if_no_ttl():
    class Foo(ExpiringRedisHash):
        key = String()

    Foo.new()
