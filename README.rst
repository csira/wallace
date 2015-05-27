.. image:: https://pypip.in/download/wallace/badge.png
    :target: https://pypi.python.org/pypi/wallace/
    :alt: Downloads

.. image:: https://pypip.in/version/wallace/badge.png
    :target: https://pypi.python.org/pypi/wallace/
    :alt: Latest Version

.. image:: https://pypip.in/license/wallace/badge.png
    :target: https://pypi.python.org/pypi/wallace/
    :alt: License


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

Wallace wraps database adapters for easy connection handling and data
modeling in Python_ apps. We extend the enterprise libraries but do not
override or replace their functionality, so performance profiles etc.
remain intact. Major features include:

* **Databases:** Currently supports PostgreSQL_ (psycopg_), Redis_ (redispy_), and MongoDB_ (pymongo_). More to come
* **Modeling:** A bare-bones ORM, built around a consistent type interface to model attributes across backends. Use of the ORM is optional, other database and config utilities can be used without it.
* **Caching:** Automatic connection pool sharing - set it and forget it


Basic Usage
~~~~~~~~~~~

To spin up a Postgres connection pool, pass DNS connection info and an optional min/max number of connections:

.. code-block:: python

  >>> from wallace import PostgresPool
  >>> dns = {'host': '/tmp/', 'database': 'postgres', 'user': 'postgres', 'password': ''}
  >>> pool = PostgresPool.construct(**dns)  # defaults to max 1 connection in the pool
  >>>
  >>> # or, specifying a max pool size:
  >>> pool = PostgresPool.construct(maxconn=5, **dns)
  >>>
  >>> # name the connection if you would like to cache it
  >>> pool = PostgresPool.construct(name='my_db', **dns)


To use the standard interface, wrap a table:

.. code-block:: python

  >>> from wallace import PostgresTable
  >>> class UserTable(PostgresTable):
  >>>     db_name = 'my_db'  # specified in `PostgresPool.construct` above
  >>>     table_name = 'user'
  >>>
  >>> UserTable.add(name='guido', email='bdfl@python.org')
  >>> UserTable.fetchall()
  [{'name': 'guido', 'email': 'bdfl@python.org'}]


And create a model to plug the table like so:

.. code-block:: python

  >>> from wallace import PostgresModel, String
  >>> class User(PostgresModel):
  >>>     table = UserTable
  >>>     name = String()
  >>>     email = String(pk=True)  # primary key field
  >>>
  >>> # models may be used to retrieve existing records,
  >>> u = User.fetch(email='bdfl@python.org')
  >>> u.name
  'guido'
  >>>
  >>> # create new ones,
  >>> newguy = User.construct(name='spacemanspiff', email='spaceman@spiff.com')
  >>> newguy.push()
  >>>
  >>> # and execute searches
  >>> [u.email for u in User.find_all(name='spacemanspiff')]
  ['spaceman@spiff.com']


*'push'* to update a model:

.. code-block:: python

  >>> u.email = 'other_guy@python.org'
  >>> u.push()
  >>>
  >>> User.fetch(email='guido@python.org')
  Traceback (most recent call last):
  ...
  wallace.db.base.errors.DoesNotExist
  >>>
  >>> print User.fetch(email='other_guy@python.org').name
  'guido'


*'delete'* to delete:

.. code-block:: python

  >>> me.delete()
  >>> User.fetch(email='other_guy@python.org')
  Traceback (most recent call last):
  ...
  wallace.db.base.errors.DoesNotExist


Download and Install
~~~~~~~~~~~~~~~~~~~~

``pip install wallace`` to install the latest stable release.


License
~~~~~~~

.. __: https://github.com/csira/wallace/raw/master/LICENSE.txt

Code, tutorials, and documentation for wallace are all open source under the BSD__ license.


*Enjoy your data.*
