from contextlib import contextmanager

unknown_sentinel = object()


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
