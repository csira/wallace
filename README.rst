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

Wallace wraps database adapters to ease connection handling and data
modeling in Python_ apps. Wallace extends the enterprise libraries
it uses, it does not override or replace their funcionality, so
the interfaces and performance profiles you're familiar with remain intact.
Major features include:

* **Databases:** Currently supports PostgreSQL_ (psycopg_), Redis_ (redispy_), and MongoDB_ (pymongo_). More to come
* **Modeling:** A bare-bones ORM, built around a consistent interface to model attributes across backends. Wallace largely consists of connection utilities and table-level abstractions so model use is optional
* **Caching:** Automatic connection pool sharing - set it and forget it


Basic Usage
~~~~~~~~~~~

To spin up a Postgres connection pool, pass DNS connection info and an optional min/max number of connections:

.. code-block:: python

  >>> from wallace import PostgresPool
  >>> dns = {'host': '/tmp/', 'database': 'postgres', 'user': 'chris', 'password': ''}
  >>> pool = PostgresPool.construct(**dns)  # defaults to max 1 connection in the pool
  >>>
  >>> # or, specifying a max pool size:
  >>> pool = PostgresPool.construct(maxconn=5, **dns)
  >>>
  >>> # also, name the connection if you would like to cache it
  >>> pool = PostgresPool.construct(name='my_db', **dns)


To use the standard interface, wrap a table:

.. code-block:: python

  >>> from wallace import PostgresTable
  >>> class UserTable(PostgresTable):
  >>>     db_name = 'my_db'  # specified in `PostgresPool.construct` above
  >>>     table_name = 'user'
  >>>
  >>> UserTable.add(name='chris', email='email@someplace.com')
  >>> UserTable.fetchall()
  [{'name': 'chris', 'email': 'email@someplace.com'}]


And create a model to plug the table like so:

.. code-block:: python

  >>> from wallace import PostgresModel, String
  >>> class User(PostgresModel):
  >>>     table = UserTable
  >>>     name = String()
  >>>     email = String(pk=True)  # primary key field
  >>>
  >>> # models may be used to retrieve existing records,
  >>> me = User.fetch(email='email@someplace.com')
  >>> me.name
  'chris'
  >>>
  >>> # create new ones,
  >>> newguy = User.construct(name='guido', email='bdfl@python.org')
  >>> newguy.push()
  >>>
  >>> # and execute searches
  >>> [u.email for u in User.find_all(name='guido')]
  ['bdfl@python.org']


Update a model by 'push'ing:

.. code-block:: python

  >>> me.email = 'new_email@somewherenew.com'
  >>> me.push()
  >>>
  >>> User.fetch(email='email@someplace.com')
  Traceback (most recent call last):
  ...
  wallace.db.base.errors.DoesNotExist
  >>>
  >>> print User.fetch(email='new_email@somewherenew.com').name
  'chris'


'delete' to delete:

.. code-block:: python

  >>> me.delete()
  >>> User.fetch(email='new_email@somewherenew.com')
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
