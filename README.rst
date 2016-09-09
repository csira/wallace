.. _Python: http://python.org/

.. _MongoDB: http://www.mongodb.com
.. _pymongo: https://pypi.python.org/pypi/pymongo

.. _PostgreSQL: http://www.postgresql.org/
.. _psycopg: https://pypi.python.org/pypi/psycopg2

.. _Redis: http://www.redis.io
.. _redispy: https://pypi.python.org/pypi/redis/


=======
Wallace
=======

Wallace is an API for modeling data with common Python_ database adaptors.

* **Databases:** Supports PostgreSQL_ (psycopg_), Redis_ (redispy_), and MongoDB_ (pymongo_). More to come.
* **Libraries:** Extends the Postgres etc. drivers but does not override them, so base interfaces and performance profiles are untouched.
* **Cache:** Automatic connection management and sharing - set it and forget it.
* **API:** A static typing interface to handle inbound and outbound typecasting (to/from db). Use middleware hooks for custom behavior.

**Please note:** version 0.9.0 is a breaking change, freeze 0.0.9 in your pip reqs file if your code relies on it. ``wallace==0.0.9``


Basic Example
~~~~~~~~~~~~~

Initialize the config and set up a connection:

.. code-block:: python

  >>> from wallace.config import App
  >>>
  >>> app = App()
  >>> app.add_postgres_connection(<dbname>, <host>, <port>, name='my_pg_conn')


Wrap a table:

.. code-block:: python

  >>> from wallace import PostgresTable
  >>>
  >>> class UserTable(PostgresTable):
  >>>
  >>>     db_name = 'my_pg_conn'
  >>>     table_name = 'user'


Model a row:

.. code-block:: python

  >>> from wallace import PostgresModel
  >>> from wallace import Integer, String
  >>>
  >>>
  >>> class User(PostgresModel):
  >>>
  >>>     table = UserTable
  >>>
  >>>     first_name = String()
  >>>     last_name = String()
  >>>     email = String(pk=True)  # primary key
  >>>     age = Integer()


Insert a row:

.. code-block:: python

  >>> user = User.construct(
  >>>     first_name='john', last_name='cleese',
  >>>     email='foo@bar.com', age=50)
  >>>
  >>> user.save()


Fetch a row:

.. code-block:: python

  >>> user = User.fetch(email='foo@bar.com')
  >>> user.first_name, user.last_name
  ('john', 'cleese')


Update, find, delete:

.. code-block:: python

  >>> user = User.fetch(email='foo@bar.com')
  >>> user.age += 1
  >>> user.save()
  >>>
  >>> [u.email for u in User.find_all(first_name='john')]
  ['foo@bar.com']
  >>>
  >>> user.delete()


Patterns, types, etc. are consistent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the same type-descriptors, connection registration, etc. for all the
database drivers wrapped by Wallace. Compare Redis here to Postgres above:

.. code-block:: python

  >>> import time
  >>> import uuid
  >>>
  >>> from wallace import ExpiringRedisHash
  >>> from wallace import Integer, Moment, Now, UUID
  >>> from wallace.config import get_app
  >>>
  >>> app = get_app()
  >>> app.add_redis_connection('0.0.0.0', port=6379, name='my_redis_conn')
  >>>
  >>> class WebSession(ExpiringRedisHash):
  >>>
  >>>     db_name = 'my_redis_conn'
  >>>     ttl = 60 * 60
  >>>
  >>>     session_id = UUID(key=True, default=lambda: uuid.uuid4())
  >>>     created_at = Now()
  >>>     last_authed_at = Moment(default=None)
  >>>     user_id = Integer(default=None)
  >>>
  >>>     def login(self, user_id):
  >>>         self.user_id = user_id
  >>>         self.last_authed_at = int(time.time())
  >>>         self.save()


Use connections directly
~~~~~~~~~~~~~~~~~~~~~~~~

Grab a registered connection and use it directly any time:

.. code-block:: python

  >>> from wallace.config import get_connection
  >>>
  >>> conn = get_connection('my_redis_conn')
  >>> with conn.pipeline() as pipe:
  >>>     pipe.rpush('mylist', 1)
  >>>     pipe.rpush('mylist', 2)
  >>>     pipe.rpush('mylist', 3)
  >>>     pipe.execute()
  >>>
  >>> print conn.lpop('mylist')
  1


Create a custom type
~~~~~~~~~~~~~~~~~~~~

Wallace comes pre-packaged with type-descriptors for some common
Python primitives. They're easy to subclass in order to achieve more specific
behavior:

.. code-block:: python

  >>> from wallace import RedisHash, Integer, String
  >>>
  >>>
  >>> class CardRank(Integer):
  >>>
  >>>     default = None
  >>>     validators = ( lambda val: val > 1, lambda val < 10, )
  >>>
  >>>
  >>> suits = ['hearts', 'spades', 'diamonds', 'clubs']
  >>>
  >>> class PlayingCard(RedisHash):
  >>>
  >>>     suit = String(validators=( lambda val: val in suits, ))
  >>>     rank = CardRank()
  >>>
  >>>     @property
  >>>     def key(self):
  >>>         return "{}-of-{}".format(rank, suit)

DataType can be subclasses directly too.

Download and Install
~~~~~~~~~~~~~~~~~~~~

The latest stable release is always on PyPI. ``pip install wallace``


*Enjoy your data.*
