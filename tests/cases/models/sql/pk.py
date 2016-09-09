from tests.utils import should_throw
from tests.utils.registry import register

from wallace.db import SqlTable, SqlModel, String, DataType, Integer
from wallace.errors import SetupError, ValidationError


class SuperTable(SqlTable):
    pass


class SuperModel(SqlModel):
    pass


@register
@should_throw(SetupError, 401)
def test_pk_reqd():
    class MyModel(SuperModel):
        pass

    MyModel.new()


@register
def test_pk():
    class MyTable(SuperTable):
        table_name = 'my_sql_table'

    class MyModel(SuperModel):
        table = MyTable
        field1 = String(pk=True)
        field2 = String(pk=True)
        filed3 = String()

    fields = sorted(list(MyModel._cbs_primary_key_fields))
    assert fields == ['field1', 'field2']


@register
def test_pks_trickle_down():
    class MyTable(SuperTable):
        table_name = 'my_sql_table'

    class MyModel(SuperModel):
        table = MyTable
        field1 = String(pk=True)
        field2 = String(pk=True)
        filed3 = String()

    class SubModel(MyModel):
        field4 = String(pk=True)
        field5 = String()

    fields = sorted(list(SubModel._cbs_primary_key_fields))
    assert fields == ['field1', 'field2', 'field4']


@register
def test_pks_override():
    class MyTable(SuperTable):
        table_name = 'my_sql_table'

    class MyModel(SuperModel):
        table = MyTable
        field1 = String(pk=True)
        field2 = String(pk=True)
        filed3 = String()

    class SubModel(MyModel):
        field2 = String()
        field4 = String(pk=True)
        field5 = String()

    fields = sorted(list(SubModel._cbs_primary_key_fields))
    assert fields == ['field1', 'field4']


@register
def test_pk_type_override():
    class MyTable(SuperTable):
        table_name = 'my_sql_table'

    class MyModel(SuperModel):
        table = MyTable
        field1 = String(pk=True)
        field2 = String(pk=True)

    class SubModel(MyModel):
        field2 = Integer(pk=True)

    assert isinstance(SubModel.__dict__['field2'], Integer)


@register
def test_compare_pk():
    class MyTable(SuperTable):
        table_name = 'my_sql_table'

    class MyModel(SuperModel):
        table = MyTable
        field1 = String(pk=True)

    inst = MyModel.construct(new=False, field1='abc')
    assert inst.primary_key == {'field1': 'abc'}

    inst.field1 = 'xyz'
    assert inst.primary_key == {'field1': 'abc'}


@register
@should_throw(ValidationError, 404)
def test_error_if_pk_field_missing():
    class MyTable(SuperTable):
        table_name = 'my_sql_table'

    class MyModel(SuperModel):
        table = MyTable
        field1 = String(pk=True)
        field2 = String(pk=True)
        field3 = String()

    inst = MyModel.construct(new=False, field1='abc', field3='xyz')
    inst.primary_key


@register
@should_throw(ValidationError, 404)
def test_error_if_pk_field_empty_str():
    class MyTable(SuperTable):
        table_name = 'my_sql_table'

    class MyModel(SuperModel):
        table = MyTable
        field1 = String(pk=True)
        field2 = String(pk=True)

    inst = MyModel.construct(new=False, field1='abc', field2='')
    inst.primary_key


@register
@should_throw(ValidationError, 404)
def test_error_if_pk_field_null():
    class MyTable(SuperTable):
        table_name = 'my_sql_table'

    class MyModel(SuperModel):
        table = MyTable
        field1 = String(pk=True)
        field2 = String(pk=True)

    inst = MyModel.construct(new=False, field1='abc', field2=None)
    inst.primary_key
