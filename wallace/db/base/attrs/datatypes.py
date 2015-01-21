import time

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
