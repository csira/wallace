from tests.utils import should_throw
from tests.utils.registry import register

from wallace.config import App, get_app, get_connection
from wallace.errors import ConfigError


@register
def test_get():
    x = App()
    y = get_app()
    assert x == y


@register
def test_get_conn():
    app = App()
    conn = app.add_redis_connection(name='my_redis_conn', host='0.0.0.0')
    assert get_connection('my_redis_conn') == conn


@register
@should_throw(ConfigError, 102)
def test_get_conn_fail():
    get_connection('my_redis_conn')


@register
def test_add_pg_conn():
    app = App()
    conn = app.add_postgres_connection('chris', '0.0.0.0', name='pg')
    assert app.get_connection('pg') == conn


@register
def test_add_redis_conn():
    app = App()
    conn = app.add_redis_connection(name='rds', host='0.0.0.0')
    assert app.get_connection('rds') == conn


# @register
# def test_add_mongo_conn():
#     app = App()
#     conn = app.add_mongo_connection(name='mongo')
#     assert app.get_connection('mongo') == conn
