from tests.cases.models.nosql.redis._setup import set_up_and_tear_down, User
from tests.utils import should_throw
from tests.utils.registry import register

from wallace.errors import DoesNotExist


@register
@set_up_and_tear_down
def test_exists():
    User.exists(first_name='marty', last_name='mcfly')


@register
@should_throw(DoesNotExist, 203)
@set_up_and_tear_down
def test_delete():
    inst = User.fetch(first_name='christopher', last_name='walken')
    inst.delete()
    del inst

    inst = User.fetch(first_name='christopher', last_name='walken')


@register
@set_up_and_tear_down
def test_pull():
    key = {'first_name': 'marty', 'last_name': 'mcfly'}
    inst1 = User.fetch(**key)
    inst2 = User.fetch(**key)

    inst1.age = inst1.age + 5
    inst1.push()

    assert inst1.age == inst2.age + 5

    inst2.pull()
    assert inst1.age == inst2.age


@register
@set_up_and_tear_down
def test_push():
    key = {'first_name': 'marty', 'last_name': 'mcfly'}
    inst = User.fetch(**key)
    inst.age = 99

    assert inst.is_modified
    assert inst.is_attr_modified('age')

    inst.push()

    assert not inst.is_modified

    inst2 = User.fetch(**key)
    assert inst2.age == 99
