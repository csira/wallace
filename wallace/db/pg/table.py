from wallace.config import GetDBConn


def escapes(**kwargs):
    columns, placeholders, values = [], [], []
    for key, val in kwargs.iteritems():
        columns.append(key)
        placeholders.append('%s')
        values.append(val)
    return columns, placeholders, tuple(values)


def postgres_escape(**kwargs):
    columns, placeholders, values = escapes(**kwargs)
    return ','.join(columns), ','.join(placeholders), values


def query_expr(separator=' AND ', **kwargs):
    columns, _, values = escapes(**kwargs)
    columns = map(lambda col: '%s=%%s' % col, columns)
    columns = separator.join(columns)
    return columns, values


def select(table_name, limit=None, **kwargs):
    where_clause, limit_clause, values = '', '', ()

    if kwargs:
        columns, values = query_expr(**kwargs)
        where_clause = 'WHERE %s' % columns
    if limit is not None:
        limit_clause = 'LIMIT %s' % limit

    cmd = 'SELECT * FROM %s %s %s;' % (table_name, where_clause, limit_clause,)
    return cmd, values


def update(table_name, new_data, **wheres):
    set_exprs, set_vals = query_expr(separator=', ', **new_data)
    where_exprs, where_vals = query_expr(**wheres)
    cmd = 'UPDATE %s SET %s WHERE %s;' % (table_name, set_exprs, where_exprs,)
    return cmd, set_vals + where_vals


def insert(table_name, **kwargs):
    columns, placeholders, values = postgres_escape(**kwargs)
    cmd = 'INSERT INTO %s (%s) VALUES (%s);'
    cmd %= (table_name, columns, placeholders,)
    return cmd, values


def remove(table_name, **kwargs):
    exprs, values = query_expr(**kwargs)
    cmd = 'DELETE FROM %s WHERE %s;' % (table_name, exprs,)
    return cmd, values


def exists(table_name, **kwargs):
    exprs, values = query_expr(**kwargs)
    cmd = 'SELECT EXISTS(SELECT 1 FROM %s WHERE %s);' % (table_name, exprs,)
    return cmd, values


class PostgresTable(object):

    db = GetDBConn()
    db_name = None
    table_name = None

    @classmethod
    def fetchone(cls, **kwargs):
        cmd, values = select(cls.table_name, **kwargs)
        return cls.db.fetchone(cmd, values)

    @classmethod
    def fetchall(cls, **kwargs):
        cmd, values = select(cls.table_name, **kwargs)
        return cls.db.fetchall(cmd, values)

    @classmethod
    def add(cls, **kwargs):
        cmd, values = insert(cls.table_name, **kwargs)
        cls.db.execute(cmd, values)

    @classmethod
    def update(cls, new_data, **kwargs):
        if not new_data:
            return
        cmd, values = update(cls.table_name, new_data, **kwargs)
        cls.db.execute(cmd, values)

    @classmethod
    def delete(cls, **kwargs):
        cmd, values = remove(cls.table_name, **kwargs)
        cls.db.execute(cmd, values)

    @classmethod
    def exists(cls, **kwargs):
        cmd, values = exists(cls.table_name, **kwargs)
        data = cls.db.fetchone(cmd, values)
        return data.get('exists')
