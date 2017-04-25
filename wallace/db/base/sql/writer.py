from wallace.errors import ValidationError


class QueryWriter(object):

    def __init__(self, table_name):
        self._table_name = table_name

    def delete(self, **kw):
        if kw:
            where_clause, values = self._build_clause(**kw)
            query = "DELETE FROM {} WHERE {};".format(self._table_name, where_clause)
        else:
            # todo: should this throw an error instead? it's more appropiate to truncate
            # the table, perhaps this is more likely than not to be a user error?
            query = "DELETE FROM {};".format(self._table_name)
            values = []

        return query.rstrip(), values

    def exists(self, **kw):
        inner_select, vals = self.select(**kw)
        query = "SELECT EXISTS({});".format(inner_select)
        return query, vals

    def insert(self, **kw):
        if not kw:
            raise ValidationError(408)

        cols, vals = zip(*kw.items())
        col_expr = ", ".join(cols)
        placeholder_expr = ", ".join(["%s"] * len(cols))
        query = "INSERT INTO %s (%s) VALUES (%s);" % (self._table_name, col_expr, placeholder_expr)
        return query, list(vals)

    def select(
            self, columns=None, limit=None, offset=None,
            separator=" AND ", order_by=None, direction="ASC", **kw):

        columns_to_fetch = ", ".join(columns) if columns else "*"
        query = "SELECT {} FROM {}".format(columns_to_fetch, self._table_name)

        limit_clause, offset_clause, order_by_clause = "", "", ""
        where_clause, values = self._build_clause(separator=separator, **kw)

        if where_clause:
            query += " WHERE {}".format(where_clause)
        if limit:
            query += " LIMIT {}".format(limit)
        if offset:
            query += " OFFSET {}".format(offset)

        if order_by:
            if isinstance(order_by, (list, tuple)):
                order_by = ", ".join(order_by)
            query += " ORDER BY {} {}".format(order_by, direction)

        return query.rstrip(), values

    def update(self, new_data, separator=" AND ", **kw):
        if not new_data:
            raise ValidationError(409)

        set_clause, set_values = self._build_clause(separator=", ", **new_data)
        where_clause, where_values = self._build_clause(separator=separator, **kw)

        query = "UPDATE {} SET {}".format(self._table_name, set_clause)
        if where_clause:
            query += " WHERE {}".format(where_clause)

        values = set_values + where_values
        return query.rstrip(), values

    @staticmethod
    def _build_clause(separator=" AND ", **kw):
        if not kw:
            return "", []

        col_exprs = []
        vals = []
        for col, val in kw.iteritems():
            col_exprs.append("{} = %s".format(col))
            vals.append(val)

        expr = separator.join(col_exprs)
        return expr, vals
