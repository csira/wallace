from wallace.db.base.middleware import Middleware


class RedisMiddleware(Middleware):

    def cast(self, data_type, val):
        if not isinstance(val, data_type):
            return data_type(val)
        return val
