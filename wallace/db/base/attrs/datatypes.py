import time
import uuid

import ujson
from wallace.db.base.attrs.base import DataType


class Boolean(DataType):

    cast = bool
    default = False

    @classmethod
    def typecast(cls, inst, val):
        if isinstance(val, basestring):
            return val == 'True' or val == 'true' or val == 't'
        return super(Boolean, cls).typecast(inst, val)


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

    @classmethod
    def typecast(cls, inst, val):
        try:
            val = cls.cast(val)
        except UnicodeDecodeError:
            val = val.decode('utf-8')
        return super(Unicode, cls).typecast(inst, val)


class JSON(String):

    def __get__(self, inst, owner):
        serialized = super(JSON, self).__get__(inst, owner)
        return ujson.loads(serialized) if serialized else serialized

    @classmethod
    def typecast(cls, inst, val):
        if val and isinstance(val, basestring):
            try:
                val = ujson.loads(val)
            except TypeError:
                if inst._cbs_is_db_data_inbound:
                    raise

        val = ujson.dumps(val) if val else val
        return super(JSON, cls).typecast(inst, val)



def is_uuid(val):
    try:
        uuid.UUID(val)
    except ValueError:
        return False
    return True


def is_uuid4(val):
    try:
        val = uuid.UUID(val)
    except ValueError:
        return False
    return val.version == 4


class UUID(String):

    validators = (is_uuid,)

    @classmethod
    def typecast(cls, inst, val):
        if isinstance(val, uuid.UUID):
            val = val.hex
        else:
            val = uuid.UUID(val).hex

        return super(UUID, cls).typecast(inst, val)


class UUID4(UUID):

    validators = (is_uuid4,)
