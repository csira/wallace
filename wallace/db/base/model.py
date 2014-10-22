from contextlib import contextmanager

from wallace.db.base.attrs import DataType
from wallace.db.base.errors import DoesNotExist


class Base(type):
    def __new__(cls, name, bases, dct):
        defaults = []
        for key, val in dct.items():
            if isinstance(val, DataType):
                val.attr = key
                if val.default:
                    defaults.append((key, val.default,))

        the_class = super(Base, cls).__new__(cls, name, bases, dct)
        the_class._cbs_default_fields = tuple(defaults)

        return the_class


class Model(object):

    __metaclass__ = Base

    @classmethod
    def fetch(cls):
        raise NotImplementedError

    @classmethod
    def new(cls):
        inst = cls()
        inst._cbs_is_new = True

        for attr, default in cls._cbs_default_fields:
            val = default() if callable(default) else default
            inst._cbs_updated[attr] = val

        return inst

    @classmethod
    def construct(cls, new=True, **kwargs):
        if new:
            inst = cls.new()
            for attr, val in kwargs.iteritems():
                setattr(inst, attr, val)
        else:
            inst = cls()
            inst._cbs_db_data = kwargs
        return inst

    def __init__(self):
        self._cbs_db_data = {}
        self._cbs_deleted = set()
        self._cbs_is_new = False
        self._cbs_updated = {}

    @property
    def is_new(self):
        return self._cbs_is_new

    @property
    def raw(self):
        data = dict(self._cbs_db_data)
        data.update(self._cbs_updated)
        for attr in self._cbs_deleted:
            data[attr] = None
        return data


    def _get_attr(self, attr):
        if attr in self._cbs_deleted:
            return None
        if attr in self._cbs_updated:
            return self._cbs_updated[attr]
        return self._cbs_db_data.get(attr)

    def _set_attr(self, attr, val):
        if attr in self._cbs_deleted:
            self._cbs_deleted.remove(attr)
        self._cbs_updated[attr] = val
        if val == self._cbs_db_data.get(attr):
            self._cbs_updated.pop(attr)

    def _del_attr(self, attr):
        if attr in self._cbs_updated:
            self._cbs_updated.pop(attr)
        if not self._cbs_is_new:
            self._cbs_deleted.add(attr)


    def pull(self):
        if self._cbs_is_new:
            raise DoesNotExist('new record, push first')
        data = self._read_data()
        if not data:
            raise DoesNotExist
        self._cbs_db_data = data

    def _read_data(self):
        raise NotImplementedError


    def push(self, *a, **kw):
        with self._write_mgr() as (state, changes,):
            self._write_data(state, changes, *a, **kw)

    @contextmanager
    def _write_mgr(self):
        state = dict(self._cbs_db_data)
        state.update(self._cbs_updated)
        changes = dict(self._cbs_updated)
        for attr in self._cbs_deleted:
            state.pop(attr, None)
            changes[attr] = None

        yield state, changes

        self._cbs_db_data = state
        self._cbs_is_new = False
        self.rollback()

    def _write_data(self, state, changes, *a, **kw):
        raise NotImplementedError


    def rollback(self):
        self._cbs_deleted = set()
        self._cbs_updated = {}

    def delete(self):
        raise NotImplementedError
