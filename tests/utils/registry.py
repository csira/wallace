import functools

from wallace.config import App
import wallace.config.cache


_cache = []
_solo = []


def get_running():
    if _solo:
        return _solo
    return _cache


def register(f):
    @functools.wraps(f)
    def wrapper():
        _refresh()
        return f()
    _cache.append(wrapper)
    return wrapper


def _refresh():
    App._inst = None
    wallace.config.cache._connection_cache = {}


def get_all_tests():
    return _cache


def solo(f):
    _solo.append(f)
    return f
