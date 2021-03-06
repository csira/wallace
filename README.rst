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

Wallace is a Python API for modeling data.
Use it to construct, manage, and manipulate domain models for
the PostgreSQL_ (psycopg_), Redis_ (redispy_), and MongoDB_ (pymongo_) database
adaptors.
It was designed to sit in the space between direct database access and
industrial strength ORMs, without abstracting away performance considerations
or making assumptions about underlying data storage.

**Please note:** version 0.9.* is a breaking change, freeze 0.0.9 in your pip reqs file if your code relies on it. ``wallace==0.0.9``


Basic SQL Example
~~~~~~~~~~~~~~~~~

Start using Wallace by configuring at least one database connection:

.. code-block:: python

  >>> from wallace.config import App
  >>>
  >>> app = App()
  >>> app.add_postgres_connection(<dbname>, <host>, <port>, name="my_pg_conn")


As an additional step for Postgres, a representation of the table is required.
(Likewise for Mongo collections.)

.. code-block:: python

  >>> from wallace import PostgresTable
  >>>
  >>> class UserTable(PostgresTable):
  >>>
  >>>     db_name = "my_pg_conn"
  >>>     table_name = "user"


Postgres models require at least one attribute be labeled as a primary key field with ``pk=True``.
Note that the table defined above is tied in as well; calls to the database will be proxied through it.

.. code-block:: python

  >>> from wallace import PostgresModel
  >>> from wallace import Integer, String
  >>>
  >>> class User(PostgresModel):
  >>>
  >>>     table = UserTable
  >>>
  >>>     first_name = String()
  >>>     last_name = String()
  >>>     email = String(pk=True)  # primary key
  >>>     age = Integer()


Use ``construct`` to create a new model instance and ``save`` to persist it:

.. code-block:: python

  >>> user = User.construct(
  >>>     first_name="john", last_name="cleese",
  >>>     email="foo@bar.com", age=50)
  >>>
  >>> user.save()


Retrieve an existing row with ``fetch``, passing in the primary key fields:

.. code-block:: python

  >>> user = User.fetch(email="foo@bar.com")
  >>> user.first_name, user.last_name
  ('john', 'cleese')


Update, find, delete:

.. code-block:: python

  >>> user = User.fetch(email="foo@bar.com")
  >>> user.age += 1
  >>> user.save()
  >>>
  >>> [u.email for u in User.find_all(first_name="john")]
  ['foo@bar.com']
  >>>
  >>> user.delete()


Consistency
~~~~~~~~~~~

The same connection registration, type descriptors, etc. are used for all the
database drivers wrapped by Wallace. Compare a Redis model:

.. code-block:: python

  >>> import time
  >>> import uuid
  >>>
  >>> from wallace import ExpiringRedisHash
  >>> from wallace import Integer, Moment, Now, UUID
  >>> from wallace.config import get_app
  >>>
  >>> app = get_app()
  >>> app.add_redis_connection("0.0.0.0", port=6379, name="my_redis_conn")
  >>>
  >>> class WebSession(ExpiringRedisHash):
  >>>
  >>>     db_name = "my_redis_conn"
  >>>     ttl = 60*60
  >>>
  >>>     session_id = UUID(key=True, default=lambda: uuid.uuid4())
  >>>     created_at = Now()
  >>>     last_authed_at = Moment()
  >>>     user_id = Integer(default=None)
  >>>
  >>>     def login(self, user_id):
  >>>         self.user_id = user_id
  >>>         self.last_authed_at = int(time.time())
  >>>         self.save()


Create a custom type
~~~~~~~~~~~~~~~~~~~~

Wallace "types" need not map directly to Python primitives. Build new ones
ad hoc, particularly to improve readability:

.. code-block:: python

  >>> from wallace import RedisHash, Boolean, String
  >>>
  >>> suits = ("hearts", "spades", "diamonds", "clubs")
  >>>
  >>>
  >>> def validate_cardrank(cardrank):
  >>>     if cardrank.isdigit():
  >>>         cardrank = int(cardrank)
  >>>         return cardrank > 1 and cardrank < 10
  >>>     return cardrank in ("J", "Q", "K", "A")
  >>>
  >>>
  >>> class CardRank(String):
  >>>
  >>>     default = None
  >>>     validators = (validate_cardrank,)
  >>>
  >>>
  >>> class PlayingCard(RedisHash):
  >>>
  >>>     # validators can also be passed directly into the attribute
  >>>     suit = String(validators=( lambda val: val in suits, ))
  >>>     rank = CardRank()
  >>>     is_joker = Boolean()
  >>>
  >>>     @property
  >>>     def key(self):
  >>>         return "joker" if self.is_joker else "{}-of-{}".format(self.rank, self.suit)


Download and Install
~~~~~~~~~~~~~~~~~~~~

The latest stable release is always on PyPI. ``pip install wallace``


*Enjoy your data.*
