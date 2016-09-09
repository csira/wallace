import functools

from tests.utils import should_throw
from tests.utils.registry import register

from wallace.db import SqlTable, SqlModel, String
from wallace.errors import SetupError


class SuperTable(SqlTable):
    pass


class SuperModel(SqlModel):
    pass


# @_insert_table(f):
#     @functools.wraps(f)
#     def wraps():
#         class MyTable(MyDriver):
#             table_name = 'my_sql_table'

#         f(MyTable)

#     return wraps


# def _insert(f):
#     @functools.wraps(f)
#     def wraps():
#         class MyDriver(SqlTable):
#             pass

#         class MyTable(MyDriver):
#             table_name = 'my_sql_table'



#         f(MySuper)
#     return wraps


@register
@should_throw(SetupError, 402)
def test_table_reqd():
    class MyModel(SuperModel):
        x = String(pk=True)

    MyModel.new()


@register
@should_throw(SetupError, 403)
def test_table_subcls():
    class FakeTable(object):
        table_name = 'my_table'

    class MyModel(SuperModel):
        table = FakeTable
        x = String(pk=True)

    MyModel.new()
