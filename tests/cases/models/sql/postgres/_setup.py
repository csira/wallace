import functools
import time

from wallace import PostgresTable, PostgresModel, Integer, String, Moment, Now
from wallace.config import App, get_app

DB_NAME = 'my_pg_conn'
TABLE_NAME = 'my_test_table'


CREATE_Q = '''
    create table {} (
        user_id int primary key,
        first_name text not null,
        last_name text,
        age int,
        created_at int,
        updated_at int
    )
    '''.format(TABLE_NAME)


def set_up_and_tear_down(f):
    @functools.wraps(f)
    def wraps():
        app = App()
        conn = app.add_postgres_connection('chris', '0.0.0.0', name=DB_NAME)
        conn.execute(CREATE_Q)  # create table
        _install_fixtures(conn)

        try:
            f()
        finally:
            conn.execute('drop table {};'.format(TABLE_NAME))

    return wraps


def _install_fixtures(conn):
    now = int(time.time())
    for uid, first_name, last_name, age in default_data:
        q = "insert into %s (user_id, first_name, last_name, age, created_at, updated_at) values ('{}', '{}', '{}', {}, {}, {})"
        q %= TABLE_NAME
        q = q.format(uid, first_name, last_name, age, now, now)
        conn.execute(q)


class UserTable(PostgresTable):

    db_name = DB_NAME
    table_name = TABLE_NAME


class User(PostgresModel):

    table = UserTable

    user_id = Integer(pk=True)
    first_name = String()
    last_name = String()
    age = Integer()

    created_at = Now()
    updated_at = Moment()

    def push(self, *a, **kw):
        self.updated_at = int(time.time())
        return super(User, self).push(*a, **kw)


default_data = [
    (1, 'marty', 'mcfly', 18),
    (2, 'christopher', 'walken', 58),
    (3, 'enrico', 'fermi', 88),
    # ('john', 'smith', 30),
    # ('matt', 'jones', 45),
    # ('jiminy', 'cricket', 70),
    # ('marty', 'wall', 55),
]
