from wallace.errors import ValidationError


class QueryWriter(object):

    def __init__(self, table_name):
        self._table_name = table_name

    def delete(self, **kw):
        where_clause, values = self._build_clause(prefix='WHERE', **kw)
        query = 'DELETE FROM {} {}'.format(self._table_name, where_clause)
        return query.rstrip(), values

    def exists(self, **kw):
        inner_select, vals = self.select(**kw)
        query = "SELECT EXISTS({})".format(inner_select)
        return query, vals

    def insert(self, **kw):
        if not kw:
            raise ValidationError(408)

        cols, vals = zip(*kw.items())
        col_expr = ', '.join(cols)
        placeholder_expr = ', '.join(['%s'] * len(cols))

        pieces = (self._table_name, col_expr, placeholder_expr)
        query = "INSERT INTO %s (%s) VALUES (%s);" % pieces
        return query, list(vals)

    def select(
            self, columns=None, limit=None, offset=None,
            operator=' AND ', order_by=None, direction='ASC', **kw):

        columns_to_fetch = ", ".join(columns) if columns else "*"
        query = 'SELECT {} FROM {}'.format(columns_to_fetch, self._table_name)

        limit_clause, offset_clause, order_by_clause = '', '', ''
        where_clause, values = self._build_clause(
            prefix='WHERE', separator=operator, **kw)

        if where_clause:
            query += ' ' + where_clause

        if limit:
            query += ' LIMIT {}'.format(limit)

        if offset:
            query += ' OFFSET {}'.format(offset)

        if order_by:
            if isinstance(order_by, (list, tuple)):
                order_by = ', '.join(order_by)

            query += ' ORDER BY {} {}'.format(order_by, direction)

        return query.rstrip(), values

    def update(self, new_data, operator=' AND ', **kw):
        if not new_data:
            raise ValidationError(409)

        where_clause, where_values = self._build_clause(
            prefix='WHERE', separator=operator, **kw)

        set_clause, set_values = self._build_clause(
            prefix='SET', separator=', ', **new_data)

        values = set_values + where_values
        pieces = (self._table_name, set_clause, where_clause)

        query = "UPDATE %s %s %s" % pieces
        return query.rstrip(), values

    @staticmethod
    def _build_clause(prefix='', separator=' AND ', **kw):
        if not kw:
            return '', []

        col_exprs = []
        vals = []
        for col, val in kw.iteritems():
            col_exprs.append('%s = %%s' % col)
            vals.append(val)

        expr = prefix + ' ' + separator.join(col_exprs)
        return expr.lstrip(), vals
