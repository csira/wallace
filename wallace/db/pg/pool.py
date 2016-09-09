from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

from wallace.config import register_connection
from wallace.errors import DBError, ValidationError


def _error_msg(err):
    # http://www.postgresql.org/docs/current/static/errcodes-appendix.html#ERRCODES-TABLE
    return '%s - %s' % (err.pgcode, err.diag.message_primary,)


def _catch(f):
    def wrap(*a, **kw):
        try:
            return f(*a, **kw)
        except psycopg2.IntegrityError, err:
            raise ValidationError(601, _error_msg(err))
        except psycopg2.Error, err:
            raise DBError(602, _error_msg(err))
    return wrap


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
        '''
        When a connection exits the with block,
            - the tx is committed if no errors were encountered
            - the tx is rolled back if errors

        When a cursor exits its with block it is closed, without affecting
        the state of the transaction.

        http://initd.org/psycopg/docs/usage.html

        '''

        with self.connection(autocommit) as conn:
            with conn.cursor() as cursor:
                yield cursor

    def transaction(self):
        return self.cursor(autocommit=False)


    @_catch
    def execute(self, cmd, values=None):
        with self.cursor() as cursor:
            cursor.execute(cmd, values)

    @_catch
    def fetchone(self, cmd, values=None):
        with self.cursor() as cursor:
            cursor.execute(cmd, values)
            return cursor.fetchone()

    @_catch
    def fetchall(self, cmd, values=None):
        with self.cursor() as cursor:
            cursor.execute(cmd, values)
            return cursor.fetchall()
