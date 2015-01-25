import time
import uuid

from wallace.db.base.attrs.base import DataType


class Boolean(DataType):

    cast = bool
    default = False

    @classmethod
    def typecast(cls, val):
        if isinstance(val, basestring):
            return val == 'True' or val == 'true'
        return super(Boolean, cls).typecast(val)


class ByteArray(DataType):

    cast = bytearray


class Float(DataType):

    cast = float
    default = 0.0


class Integer(DataType):

    cast = int
    default = 0


class Moment(Integer):

    default = None


class Now(Moment):

    default = lambda: int(time.time())


class String(DataType):

    cast = str


class Unicode(DataType):

    cast = unicode


class UUID(String):

    default = lambda: uuid.uuid4().hex
    validators = (
        lambda val: len(val) == 32,
        lambda val: val[12] == '4',
        lambda val: val[16] in ('8', '9', 'a', 'b',),
    )

    def __set__(self, inst, val):
        if isinstance(val, uuid.UUID):
            val = val.hex
        super(UUID, self).__set__(inst, val)
