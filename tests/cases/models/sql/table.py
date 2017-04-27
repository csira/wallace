from tests.utils import should_throw
from tests.utils.registry import register

from wallace.db import SqlTable
from wallace.errors import SetupError, WallaceError


@register
@should_throw(SetupError, 405)
def test_table_name_reqd():
    class MyDriver(SqlTable):
        pass

    class MyTable(MyDriver):
        db_name = 'db'

    MyTable.delete()


@register
def test_writer_detached():
    class MyDriver(SqlTable):
        pass

    class MyTable(MyDriver):
        table_name = 'foo'

    assert not MyTable._query_writer


@register
def test_writer_attached():
    class MyDriver(SqlTable):
        pass

    class MyTable(MyDriver):
        table_name = 'foo'

    MyTable._for_testing_only()

    assert MyTable._query_writer


@register
@should_throw(WallaceError, 410)
def test_full_delete_fails():
    class MyTable(SqlTable):
        table_name = 'foo'

    MyTable.delete()
