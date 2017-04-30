class ModelInterface(object):

    def __init__(self, pk=False, key=False, default=None):
        self.attr = None
        self.is_pk = pk
        self.is_key = key
        self.default = default

    def __get__(self, inst, _):
        return inst._getattr(self.attr)

    def __set__(self, inst, val):
        inst._setattr(self.attr, val)

    def __delete__(self, inst):
        inst._delattr(self.attr)
