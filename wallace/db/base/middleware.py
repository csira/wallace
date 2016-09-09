import abc

from wallace.errors import ConfigError


class Middleware(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, **kw):
        self.config = kw

    def __getattr__(self, key):
        try:
            return self.config[key]
        except KeyError:
            raise AttributeError

    @abc.abstractmethod
    def cast(self, data_type, val):
        return val
