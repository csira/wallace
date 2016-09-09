from tests.cases.models.sql.postgres._setup import set_up_and_tear_down, User
from tests.utils import should_throw
from tests.utils.registry import register

from wallace import PostgresTable, PostgresModel
from wallace.errors import DoesNotExist, ValidationError


@register
@set_up_and_tear_down
def test_exists():
    User.exists(first_name='marty')


@register
@set_up_and_tear_down
def test_fetch():
    inst = User.fetch(user_id=2)
    assert inst.first_name == 'christopher'


@register
@set_up_and_tear_down
@should_throw(DoesNotExist, 203)
def test_delete():
    inst = User.fetch(user_id=3)
    inst.delete()
    del inst

    inst = User.fetch(user_id=3)


@register
@set_up_and_tear_down
def test_find_one():
    inst = User.find_one(user_id=1)
    assert inst.first_name == 'marty'


@register
@set_up_and_tear_down
@should_throw(ValidationError, 407)
def test_find_one_without_params():
    inst = User.find_one()


@register
@set_up_and_tear_down
def test_pull():
    inst1 = User.fetch(user_id=1)
    inst2 = User.fetch(user_id=1)

    inst1.age = inst1.age + 5
    inst1.push()

    assert inst1.age == inst2.age + 5

    inst2.pull()
    assert inst1.age == inst2.age


@register
@set_up_and_tear_down
def test_push():
    inst = User.fetch(user_id=1)
    inst.age = 99

    assert inst.is_modified
    assert inst.is_attr_modified('age')

    inst.push()

    assert not inst.is_modified

    inst2 = User.fetch(user_id=1)
    assert inst2.age == 99
