import ujson

from wallace.config.obj import App


_app = None


def _deserialize(filename):
    with open(filename, 'r') as f:
        data = f.read()
        return ujson.loads(data)


def setup_app(filename=None, struct=None):
    if filename:
        data = _deserialize(filename)
    else:
        data = struct or {}

    global _app
    _app = App(**data)
    return _app


def get_app():
    return _app
