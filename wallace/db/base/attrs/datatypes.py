import time
import uuid

import ujson

from wallace.db.base.attrs.base import DataType
from wallace.errors import ValidationError


class Array(DataType):

    default = lambda: []
    data_type = list

    @staticmethod
    def cast_to_type(val):
        if isinstance(val, tuple):
            return list(val)
        raise ValidationError(308)


class Boolean(DataType):

    default = False
    data_type = bool

    @staticmethod
    def cast_to_type(val):
        if isinstance(val, int) or isinstance(val, float):
            if val == 0:
                return False
            elif val == 1:
                return True

        raise ValidationError(308)


class ByteArray(DataType):

    default = bytearray(b'')
    data_type = bytearray


class Float(DataType):

    default = 0.0
    data_type = float

    @staticmethod
    def cast_to_type(val):
        if isinstance(val, int):
            return float(val)
        raise ValidationError(308)


class Integer(DataType):

    default = 0
    data_type = int

    @staticmethod
    def cast_to_type(val):
        if isinstance(val, float):
            if int(val) == val:
                return int(val)
        raise ValidationError(308)


class Moment(Integer):

    default = None


class Now(Moment):

    default = lambda: int(time.time())


class String(DataType):

    default = ""
    data_type = str

    @staticmethod
    def cast_to_type(val):
        if isinstance(val, basestring):
            return str(val)
        raise ValidationError(308)


class Unicode(DataType):

    default = u""
    data_type = unicode

    @staticmethod
    def cast_to_type(val):
        if not isinstance(val, basestring):
            raise ValidationError(308)

        try:
            return unicode(val)
        except UnicodeDecodeError:
            return val.decode('utf-8')


class JSON(String):

    def __get__(self, inst, owner):
        serialized = super(JSON, self).__get__(inst, owner)
        return ujson.loads(serialized) if serialized else serialized

    @staticmethod
    def cast_to_type(val):
        return ujson.dumps(val)


def is_uuid(val):
    try:
        uuid.UUID(val)
    except ValueError:
        return False
    return True


class UUID(String):

    default = None
    validators = (is_uuid,)

    @staticmethod
    def cast_to_type(val):
        return val.hex if isinstance(val, uuid.UUID) else uuid.UUID(val).hex
