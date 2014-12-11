from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

from wallace.config import register_connection


class PostgresPool(ThreadedConnectionPool):

    @classmethod
    def construct(cls, name=None, minconn=1, maxconn=1, **kwargs):
        pool = cls(minconn, maxconn, cursor_factory=RealDictCursor, **kwargs)
        if name:
            register_connection(name, pool)
        return pool


    def getconn(self, autocommit=True, **kwargs):
        # Since any query begins a transaction when autocommit=False, the
        # session wrapped by this connection will remain 'idle in tx'
        # (potentially hang on to locks, etc.) until the caller commits.
        # Hence, we're defaulting to autocommit=True.
        conn = super(PostgresPool, self).getconn(**kwargs)
        conn.autocommit = autocommit
        return conn

    def putconn(self, conn, **kwargs):
        conn.rollback()  # todo does psycopg handle the rollback yet?
        conn.autocommit = True
        super(PostgresPool, self).putconn(conn, **kwargs)


    @contextmanager
    def connection(self, autocommit=True):
        conn = self.getconn(autocommit)
        try:
            yield conn
        finally:
            if not conn.closed:  # short circuit the PoolError
                self.putconn(conn)

    @contextmanager
    def cursor(self, autocommit=True):
        with self.connection(autocommit) as conn:
            yield conn.cursor()
            conn.commit()

    def transaction(self):
        return self.cursor(autocommit=False)


    def execute(self, cmd, values=None):
        with self.cursor() as cursor:
            cursor.execute(cmd, values)

    def fetchone(self, cmd, values=None):
        with self.cursor() as cursor:
            cursor.execute(cmd, values)
            return cursor.fetchone()

    def fetchall(self, cmd, values=None):
        with self.cursor() as cursor:
            cursor.execute(cmd, values)
            return cursor.fetchall()
