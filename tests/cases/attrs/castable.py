import uuid

from tests.utils.registry import register

from wallace import Array, Boolean, ByteArray, Float, Integer, JSON, Moment
from wallace import Now, String, Unicode, UUID


uid1 = uuid.uuid1()
uid_val1 = uuid.uuid1().hex

uid4 = uuid.uuid4()
uid_val4 = uuid.uuid4().hex


CASTABLE = [
    (Array, ([], []), ([1, 2, 3], [1, 2, 3]), ((1, 2), [1, 2])),
    # (Boolean, (True, True), (0, False), (0.0, False), (1, True)),
    (Float, (1.0, 1.0), (3.4, 3.4), (1, 1.0)),
    (Integer, (7, 7), (5.0, 5), ('2', 2)),
    (JSON, ),
    (String, ('abc', 'abc'), ('', ''), (r'abc', 'abc')),
    (Unicode, (u"abc", u"abc"), ('abc', u'abc'), (r'abc', u'abc')),
    (UUID, (uid1, uid1.hex), (uid_val1, uid_val1), (uid4, uid4.hex), (uid_val4, uid_val4)),
]


def create_test(cls, test_val, expected):
    @register
    def test_cast_success():
        cls.before_set(test_val) == expected


for item in CASTABLE:
    cls = item[0]
    for (test_val, expected) in item[1:]:
        create_test(cls, test_val, expected)
