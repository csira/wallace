from wallace.errors import ConfigError


_connection_cache = {}


def get_connection(name, silent=False):
    conn = _connection_cache.get(name)
    if not conn and not silent:
        raise ConfigError(102, 'db "%s" not registered' % name)
    return conn


def register_connection(name, obj):
    _connection_cache[name] = obj
