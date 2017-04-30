from contextlib import contextmanager

from wallace.db.base.attrs.base import DataType
from wallace.errors import DoesNotExist


def _get_default_fields(bases, dct):
    """
    Find model attributes with default values. The metaclass below adds them
    to class scope so new instances initialize with the presets.

    Merges in superclass defaults as well.

    """
    defaults = {}

    for base in bases:  # for model inheritance
        for key, val in getattr(base, "_cbs_default_fields", []):
            defaults[key] = val

    for key, val in dct.iteritems():
        if isinstance(val, DataType) and val.default is not None:
            defaults[key] = val.default
        elif key in defaults:  # catch superclass fields originally declared with
            defaults.pop(key)  # a default, but overridden here without one

    return tuple(defaults.items())


class Base(type):

    def __new__(cls, name, bases, dct):
        for key, val in dct.iteritems():
            if isinstance(val, DataType):
                val.attr = key

        the_class = super(Base, cls).__new__(cls, name, bases, dct)
        the_class._cbs_default_fields = _get_default_fields(bases, dct)
        return the_class


class ModelState(object):

    def __init__(self):
        self._cbs_db_data = dict()
        self._cbs_updated = dict()
        self._cbs_deleted = set()

        self._cbs_is_new = False
        self._cbs_is_db_data_inbound = False

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

    @property
    def diff(self):
        data = dict(self._cbs_updated)
        for attr in self._cbs_deleted:
            data[attr] = None
        return data

    def multiset(self, **kw):
        for attr, val in kw.iteritems():
            setattr(self, attr, val)

    def rollback(self):
        self._cbs_updated = dict()
        self._cbs_deleted = set()

    def _getattr(self, attr):
        if attr in self._cbs_deleted:
            return None
        if attr in self._cbs_updated:
            return self._cbs_updated[attr]
        return self._cbs_db_data.get(attr)

    def _setattr(self, attr, val):
        if self._cbs_is_db_data_inbound:
            self._cbs_db_data[attr] = val
        else:
            if val != self._cbs_db_data.get(attr):
                self._cbs_updated[attr] = val
            if attr in self._cbs_deleted:
                self._cbs_deleted.remove(attr)

    def _delattr(self, attr):
        if attr in self._cbs_updated:
            self._cbs_updated.pop(attr)
        if not self.is_new and not self._cbs_is_db_data_inbound:
            self._cbs_deleted.add(attr)

    @contextmanager
    def _protect_state(self):
        state = self.raw
        for attr in self._cbs_deleted:
            state.pop(attr, None)

        yield state, self.diff

        self._cbs_db_data = state
        self._cbs_is_new = False
        self.rollback()

    @contextmanager
    def _inbound(self):
        self._cbs_is_db_data_inbound = True
        self.rollback()
        try:
            yield
        finally:
            self._cbs_is_db_data_inbound = False


class Model(ModelState):

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
    def construct(cls, new=True, **kw):
        if new:
            inst = cls.new()
            inst.multiset(**kw)
        else:
            inst = cls()
            with inst._inbound():
                inst.multiset(**kw)
        return inst

    @classmethod
    def exists(cls, **kw):
        raise NotImplementedError


    def refresh(self, **kw):
        self.pull(**kw)

    def pull(self, **kw):
        if self.is_new:
            raise DoesNotExist(201, 'new record, does not exist in DB')

        data = self.read_from_db(**kw)
        if not data:
            raise DoesNotExist(203)

        with self._inbound():
            self.multiset(**data)

    def read_from_db(self, **kw):
        raise NotImplementedError

    def save(self, **kw):
        self.push(**kw)

    def push(self, **kw):
        with self._protect_state() as (state, changes,):
            self.write_to_db(state, changes, **kw)

    def write_to_db(self, state, changes, **kw):
        raise NotImplementedError

    def delete(self):
        if self.is_new:
            raise DoesNotExist(202, 'new model')
