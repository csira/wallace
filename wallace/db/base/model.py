from contextlib import contextmanager

from wallace.db.base.attrs import DataType
from wallace.db.base.errors import DoesNotExist


class Base(type):
    def __new__(cls, name, bases, dct):
        for key, val in dct.iteritems():
            if isinstance(val, DataType):
                val.attr = key

        the_class = super(Base, cls).__new__(cls, name, bases, dct)
        the_class._cbs_default_fields = cls._get_defaults(bases, dct)
        return the_class

    @staticmethod
    def _get_defaults(bases, dct):
        defaults = {}

        for base in bases:  # handle model inheritance
            for key, val in getattr(base, '_cbs_default_fields', []):
                defaults[key] = val

        for key, val in dct.iteritems():
            if isinstance(val, DataType) and val.default is not None:
                defaults[key] = val.default
            elif key in defaults:  # catch superclass fields declared with a
                defaults.pop(key)  # default but overridden without one here

        return tuple(defaults.items())


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
            setattr(inst, attr, val)

        return inst

    @classmethod
    def construct(cls, new=True, **kwargs):
        if new:
            inst = cls.new()
            inst._set_multiple_values(**kwargs)
        else:
            inst = cls()
            inst._set_inbound_db_data(**kwargs)
        return inst

    def __init__(self):
        self._cbs_db_data = {}
        self._cbs_deleted = set()
        self._cbs_is_db_data_inbound = False
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


    @contextmanager
    def _guard_state_for_inbound_db_data(self):
        self._cbs_is_db_data_inbound = True
        try:
            yield
        finally:
            self._cbs_is_db_data_inbound = False

    def _set_multiple_values(self, **kwargs):
        for attr, val in kwargs.iteritems():
            setattr(self, attr, val)

    def _set_inbound_db_data(self, **kwargs):
        with self._guard_state_for_inbound_db_data():
            self._set_multiple_values(**kwargs)

    def multiset(self, **kwargs):
        self._set_multiple_values(**kwargs)


    def _get_attr(self, attr):
        if attr in self._cbs_deleted:
            return None
        if attr in self._cbs_updated:
            return self._cbs_updated[attr]
        return self._cbs_db_data.get(attr)

    def _set_attr(self, attr, val):
        if self._cbs_is_db_data_inbound:
            self._cbs_db_data[attr] = val
            if val == self._cbs_updated.get(attr):
                self._cbs_updated.pop(attr)

        else:
            self._cbs_updated[attr] = val
            if val == self._cbs_db_data.get(attr):
                self._cbs_updated.pop(attr)

            if attr in self._cbs_deleted:
                self._cbs_deleted.remove(attr)

    def _del_attr(self, attr):
        if attr in self._cbs_updated:
            self._cbs_updated.pop(attr)

        if not self._cbs_is_new and not self._cbs_is_db_data_inbound:
            self._cbs_deleted.add(attr)


    def pull(self):
        if self._cbs_is_new:
            raise DoesNotExist('new record, push first')

        data = self._read_data()
        if not data:
            raise DoesNotExist

        self._set_inbound_db_data(**data)

    def _read_data(self):
        raise NotImplementedError


    def push(self, *a, **kw):
        with self._state_mgr_for_writes() as (state, changes,):
            self._write_data(state, changes, *a, **kw)

    @contextmanager
    def _state_mgr_for_writes(self):
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
