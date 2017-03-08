import time
import uuid

import ujson

from wallace.db.base.attrs.base import DataType
from wallace.errors import ValidationError


class Array(DataType):

    default = lambda: []
    data_type = list

    @staticmethod
    def before_set(val):
        return list(val) if isinstance(val, tuple) else val


class Boolean(DataType):

    default = False
    data_type = bool
    nullable = False


class ByteArray(DataType):

    default = bytearray(b'')
    data_type = bytearray


class Float(DataType):

    default = 0.0
    data_type = float

    @staticmethod
    def before_set(val):
        return float(val) if not isinstance(val, float) else val


class Integer(DataType):

    default = 0
    data_type = int

    @staticmethod
    def before_set(val):
        if isinstance(val, float):
            if int(val) == val:
                return int(val)
        return int(val)


class Moment(Integer):

    default = None


class Now(Moment):

    default = lambda: int(time.time())
    nullable = False


class String(DataType):

    default = ""
    data_type = str


class Unicode(DataType):

    default = u""
    data_type = unicode

    @staticmethod
    def before_set(val):
        if not isinstance(val, basestring):
            raise ValidationError(304)

        try:
            return unicode(val)
        except UnicodeDecodeError:
            return val.decode('utf-8')


class JSON(String):

    @staticmethod
    def after_get(serialized):
        return ujson.loads(serialized) if serialized else serialized

    @staticmethod
    def before_set(val):
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
    def before_set(val):
        return val.hex if isinstance(val, uuid.UUID) else uuid.UUID(val).hex
