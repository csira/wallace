import functools
import time

from wallace import RedisHash, Integer, String, Moment, Now
from wallace.config import App, get_app

DB_NAME = 'my_redis_conn'


def set_up_and_tear_down(f):
    @functools.wraps(f)
    def wrap(*a, **kw):
        app = App()
        conn = app.add_redis_connection('0.0.0.0', name=DB_NAME)
        _install_fixtures(conn)

        try:
            f()
        finally:
            conn.flushall()

    return wrap


def _install_fixtures(conn):
    now = int(time.time())
    with conn.pipeline() as pipe:
        for uid, first_name, last_name, age in default_data:
            key = '{}|{}'.format(first_name, last_name)
            pipe.hmset(key, {
                'user_id': uid, 'first_name': first_name, 'last_name': last_name,
                'age': age, 'created_at': now, 'updated_at': now})
        pipe.execute()


class User(RedisHash):

    db_name = DB_NAME

    user_id = Integer()
    first_name = String()
    last_name = String()
    age = Integer()

    created_at = Now()
    updated_at = Moment()

    def push(self, *a, **kw):
        self.updated_at = int(time.time())
        return super(User, self).push(*a, **kw)

    @property
    def key(self):
        return '{}|{}'.format(self.first_name, self.last_name)


default_data = [
    (1, 'marty', 'mcfly', 18),
    (2, 'christopher', 'walken', 58),
    (3, 'enrico', 'fermi', 88),
]
