from tests.utils import should_throw
from tests.utils.registry import register

from wallace.config import App, get_app, get_connection
from wallace.config import GetApp, GetDBConn, GetParameter
from wallace.errors import ConfigError


@register
def test_get_app():
    app = App()

    class Test(object):
        app = GetApp()

    assert app == Test.app and app is not None


@register
def test_get_app2():
    class Test(object):
        app = GetApp()

    assert Test.app is None


@register
def test_get_conn():
    app = App()
    conn = app.add_redis_connection(name='my_redis_conn', host='0.0.0.0')

    class Test(object):
        db_name = 'my_redis_conn'
        db = GetDBConn()

    assert Test.db == conn


@register
@should_throw(ConfigError, 102)
def test_get_conn2():
    App()

    class Test(object):
        db_name = 'my_redis_conn'
        db = GetDBConn()

    Test.db


@register
def test_get_param():
    App(x=1)

    class Test(object):
        my_param = GetParameter('x')

    assert Test.my_param == 1


@register
@should_throw(ConfigError, 101)
def test_get_param2():
    App()

    class Test(object):
        my_param = GetParameter('x')

    Test.my_param
