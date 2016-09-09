class ModelInterface(object):

    default = None

    def __init__(self, pk=False, key=False, default=None):
        self.attr = None
        self.is_pk = pk
        self.is_key = key

        if default is not None:
            self.default = default

    def __get__(self, inst, owner):
        return inst._get_attr(self.attr)

    def __set__(self, inst, val):
        inst._set_attr(self.attr, val)

    def __delete__(self, inst):
        inst._del_attr(self.attr)
