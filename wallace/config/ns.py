import ujson

from wallace.config.errors import ConfigError
from wallace.config.obj import App


_app = App()


def _deserialize(filename):
    with open(filename, 'r') as f:
        data = f.read()
        return ujson.loads(data)


def setup_app(config):
    if isinstance(config, str):
        data = _deserialize(config)
    elif isinstance(config, dict):
        data = config
    else:
        raise ConfigError('must provide a filename or dictionary')

    global _app
    _app = App(**data)
    return _app


def get_app():
    return _app
