from wallace.db.base.model.meta import Base
from wallace.db.base.model.state import ModelState, unknown_sentinel
from wallace.errors import DoesNotExist


class Model(object):

    __metaclass__ = Base

    middleware = None

    @classmethod
    def new(cls):
        inst = cls(_is_new=True)

        for attr, default in cls._default_fields:
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
