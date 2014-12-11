from wallace.config.errors import ConfigError


_db_conn_cache = {}


def _throw_dne_error(name):
    raise ConfigError('db "%s" not registered' % name)


def destroy_connection(name):
    try:
        _db_conn_cache.pop(name)
    except KeyError:
        _throw_dne_error(name)


def get_connection(name, silent=False):
    conn = _db_conn_cache.get(name)
    if not conn and not silent:
        _throw_dne_error(name)
    return conn


def register_connection(name, obj):
    _db_conn_cache[name] = obj
