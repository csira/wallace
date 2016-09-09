from tests.utils.registry import register

from wallace import ValidationError
from wallace.db.base.sql.writer import QueryWriter

Writer = QueryWriter('testtable')


def is_error_caught(err, func, *a, **kw):
    try:
        func(*a, **kw)
    except err:
        return True
    else:
        return False


@register
def delete():
    assert Writer.delete() == ('DELETE FROM testtable', [])
    assert Writer.delete(a=1) == ('DELETE FROM testtable WHERE a = %s', [1])
    assert Writer.delete(a=1, b=2) == ('DELETE FROM testtable WHERE a = %s AND b = %s', [1, 2])


@register
def exists():
    assert Writer.exists() == ('SELECT EXISTS(SELECT * FROM testtable)', [])
    assert Writer.exists(a=1) == ('SELECT EXISTS(SELECT * FROM testtable WHERE a = %s)', [1])
    assert Writer.exists(a=1, b=2) == ('SELECT EXISTS(SELECT * FROM testtable WHERE a = %s AND b = %s)', [1,2])
    assert Writer.exists(columns=['foo'], a=1, b=2) == ('SELECT EXISTS(SELECT foo FROM testtable WHERE a = %s AND b = %s)', [1,2])


@register
def insert():
    assert is_error_caught(ValidationError, Writer.insert)
    assert Writer.insert(a=1) == ('INSERT INTO testtable (a) VALUES (%s);', [1])
    assert Writer.insert(a=1, b=2) == ('INSERT INTO testtable (a, b) VALUES (%s, %s);', [1, 2])


@register
def select():
    assert Writer.select() == ('SELECT * FROM testtable', [])
    assert Writer.select(columns=['a', 'b']) == ('SELECT a, b FROM testtable', [])
    assert Writer.select(limit=10, order_by='z', direction='DESC') == ('SELECT * FROM testtable LIMIT 10 ORDER BY z DESC', [])


@register
def select_multi_order():
    assert Writer.select(order_by=('x', 'y', 'z'), direction='DESC') == ('SELECT * FROM testtable ORDER BY x, y, z DESC', [])


@register
def update():
    assert is_error_caught(ValidationError, Writer.update, {})
    assert Writer.update({'a': 1, 'b': 2}) == ('UPDATE testtable SET a = %s, b = %s', [1, 2])
    assert Writer.update({'a': 1, 'b': 2}, c=3, d=4) == ('UPDATE testtable SET a = %s, b = %s WHERE c = %s AND d = %s', [1, 2, 3, 4])
