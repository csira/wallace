from contextlib import contextmanager

from wallace.db.base.attrs.base import DataType
from wallace.errors import DoesNotExist

unknown_sentinel = object()


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

    def __init__(self, is_new):
        self.db_state = dict()
        self.updated_attrs = dict()
        self.deleted_attrs = set()

        if is_new == unknown_sentinel or not isinstance(is_new, bool):
            raise Exception("use Model.new to create a new model")

        self._is_new = is_new
        self._db_data_inbound = False

    @property
    def is_new(self):
        return self._is_new

    @property
    def is_modified(self):
        return not self.is_new and (self.deleted_attrs or self.updated_attrs)

    def is_attr_modified(self, attr):
        return not self.is_new and (attr in self.deleted_attrs or attr in self.updated_attrs)

    @property
    def raw(self):
        data = dict(self.db_state)
        data.update(self.updated_attrs)
        for attr in self.deleted_attrs:
            data[attr] = None
        return data

    @property
    def diff(self):
        data = dict(self.updated_attrs)
        for attr in self.deleted_attrs:
            data[attr] = None
        return data

    def rollback(self):
        self.updated_attrs = dict()
        self.deleted_attrs = set()

    def _getattr(self, attr):
        if attr in self.deleted_attrs:
            return None
        if attr in self.updated_attrs:
            return self.updated_attrs[attr]
        return self.db_state.get(attr)

    def _setattr(self, attr, val):
        if self._db_data_inbound:
            self.db_state[attr] = val
        else:
            if val != self.db_state.get(attr):
                self.updated_attrs[attr] = val
            if attr in self.deleted_attrs:
                self.deleted_attrs.remove(attr)

    def _delattr(self, attr):
        if attr in self.updated_attrs:
            self.updated_attrs.pop(attr)
        if not self.is_new and not self._db_data_inbound:
            self.deleted_attrs.add(attr)

    @contextmanager
    def protect_state(self):
        state = self.raw
        for attr in self.deleted_attrs:
            state.pop(attr, None)

        yield state, self.diff

        self.db_state = state
        self._is_new = False
        self.rollback()

    @contextmanager
    def inbound(self):
        self._db_data_inbound = True
        self.rollback()
        try:
            yield
        finally:
            self._db_data_inbound = False


class Model(object):

    __metaclass__ = Base

    middleware = None

    @classmethod
    def new(cls):
        inst = cls(_is_new=True)

        for attr, default in cls._cbs_default_fields:
            val = default() if callable(default) else default
            setattr(inst, attr, val)

        return inst

    @classmethod
    def fetch(cls, **kw):
        inst = cls.construct(**kw)
        inst.pull()
        return inst

    @classmethod
    def construct(cls, **kw):
        inst = cls(_is_new=False)
        with inst._state.inbound():
            inst.multiset(**kw)
        return inst

    @classmethod
    def exists(cls, **kw):
        raise NotImplementedError


    def __init__(self, _is_new=unknown_sentinel):
        self._state = ModelState(_is_new)

    @property
    def raw(self):
        return self._state.raw

    @property
    def diff(self):
        return self._state.diff

    @property
    def is_new(self):
        return self._state.is_new

    @property
    def is_modified(self):
        return self._state.is_modified

    def is_attr_modified(self, attr):
        return self._state.is_attr_modified(attr)

    def rollback(self):
        self._state.rollback()


    def multiset(self, **kw):
        for attr, val in kw.iteritems():
            setattr(self, attr, val)


    def refresh(self, **kw):
        self.pull(**kw)

    # def load(self, **kw):
    #     self.pull(**kw)

    def pull(self, **kw):
        if self.is_new:
            raise DoesNotExist(201, 'new record, does not exist in DB')

        data = self.read_from_db(**kw)
        if not data:
            raise DoesNotExist(203)

        with self._state.inbound():
            self.multiset(**data)

    def read_from_db(self, **kw):
        raise NotImplementedError

    def save(self, **kw):
        self.push(**kw)

    def push(self, **kw):
        with self._state.protect_state() as (state, changes,):
            self.write_to_db(state, changes, **kw)

    def write_to_db(self, state, changes, **kw):
        raise NotImplementedError

    def delete(self):
        if self.is_new:
            raise DoesNotExist(202, 'new model')
