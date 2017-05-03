from wallace.db.base.attrs.base import DataType


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
