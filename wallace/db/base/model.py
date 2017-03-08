from contextlib import contextmanager

from wallace.db.base.attrs.base import DataType
from wallace.errors import DoesNotExist


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

        for base in bases:  # for model inheritance
            for key, val in getattr(base, '_cbs_default_fields', []):
                defaults[key] = val

        for key, val in dct.iteritems():
            if isinstance(val, DataType) and val.default is not None:
                defaults[key] = val.default
            elif key in defaults:  # catch superclass fields declared with a
                defaults.pop(key)  # default but overridden without one

        return tuple(defaults.items())


class Model(object):

    __metaclass__ = Base

    middleware = None

    @classmethod
    def new(cls):
        inst = cls()
        inst._cbs_is_new = True

        for attr, default in cls._cbs_default_fields:
            val = default() if callable(default) else default
            setattr(inst, attr, val)

        return inst

    @classmethod
    def fetch(cls, **kw):
        inst = cls.construct(new=False, **kw)
        inst.pull()
        return inst

    @classmethod
    def construct(cls, new=True, **kwargs):
        if new:
            inst = cls.new()
            inst.multiset(**kwargs)
        else:
            inst = cls()
            inst._set_inbound_db_data(**kwargs)
        return inst

    @classmethod
    def exists(cls, **kw):
        raise NotImplementedError

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
    def is_modified(self):
        return not self.is_new and (self._cbs_deleted or self._cbs_updated)

    def is_attr_modified(self, attr):
        return not self.is_new and (attr in self._cbs_deleted or attr in self._cbs_updated)

    @property
    def raw(self):
        data = dict(self._cbs_db_data)
        data.update(self._cbs_updated)
        for attr in self._cbs_deleted:
            data[attr] = None
        return data

    def multiset(self, **kwargs):
        for attr, val in kwargs.iteritems():
            setattr(self, attr, val)
        return self


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

        if not self.is_new and not self._cbs_is_db_data_inbound:
            self._cbs_deleted.add(attr)


    def reload(self, **kw):
        self.pull(**kw)

    def pull(self, **kw):
        if self.is_new:
            raise DoesNotExist(201, 'new record, does not exist in DB')

        data = self.read_from_db(**kw)
        if not data:
            raise DoesNotExist(203)

        self._set_inbound_db_data(**data)

    def read_from_db(self, **kw):
        raise NotImplementedError


    def save(self, **kw):
        self.push(**kw)

    def push(self, **kw):
        with self._protect_internal_state() as (state, changes,):
            self.write_to_db(state, changes, **kw)

    @contextmanager
    def _protect_internal_state(self):
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

    def write_to_db(self, state, changes, **kw):
        raise NotImplementedError


    def rollback(self):
        self._cbs_deleted = set()
        self._cbs_updated = {}

    def delete(self):
        if self.is_new:
            raise DoesNotExist(202, 'new model')


    def _set_inbound_db_data(self, **kw):
        self._cbs_is_db_data_inbound = True
        try:
            self.multiset(**kw)
        finally:
            self._cbs_is_db_data_inbound = False
