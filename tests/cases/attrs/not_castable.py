from tests.utils import should_throw
from tests.utils.registry import register

from wallace import Array, Boolean, ByteArray, Float, Integer, JSON, Moment
from wallace import Now, String, Unicode, UUID
from wallace.errors import ValidationError


NOT_CASTABLE = [
    (Array, 1, '123', '', {}, "[1, 2, 3]"),
    (Boolean, (), [], {}, 'True', 2, ''),
    (Float, '', 'abc', [],),
    (Integer, '4.1', 'abc', [],),
    (String, 1, 4.2, [], {}, ),
    (Unicode, 1, [], {}),
]


def create_test(cls, val):
    @register
    @should_throw(ValidationError, 304)
    def test_cast_fails():
        cls._for_testing_inbound(val)


for item in NOT_CASTABLE:
    test_cls = item[0]
    for test_val in item[1:]:
        create_test(test_cls, test_val)


@register
@should_throw(AttributeError)
def test_uuid1():
    UUID._for_testing_inbound(1)


@register
@should_throw(AttributeError)
def test_uuid2():
    UUID._for_testing_inbound([])
