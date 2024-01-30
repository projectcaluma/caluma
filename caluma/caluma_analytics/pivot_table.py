from __future__ import annotations  # self-referencing annotations

from collections import defaultdict
from functools import cached_property

from django.db import connection
from psycopg.rows import dict_row

from . import simple_table, sql

FUNCTION_PARAMETER_CAST = {
    "sum": "::float",
    "avg": "::float",
}


class PivotTable(simple_table.SQLAliasMixin):
    class _AnonymousInfo:
        """
        Pseudo GraphQL info object.

        Used for commandline access, so the commandline version
        can also invoke the visibilities.
        """

        context = {}

    def __init__(self, table, info=_AnonymousInfo):
        self.info = info

        self.table = table
        self.last_query = None
        self.last_query_params = None
        self.base_table = simple_table.SimpleTable(self.table, info=info)
        self._summary = defaultdict(int)

    @cached_property
    def _fields(self):
        fields = self.table.fields.all()

        return list(fields)

    def get_sql_and_params(self):
        """Return a list of records as specified in the given table config."""

        group_by = []

        # We replace the selects from the analytics query with
        # the aggregate function calls as required, but leave the
        # rest intact. This way, we won't need to build a subquery
        # around the whole thing and keep it relatively (!) simple
        aggregate_query = self.base_table.get_query_object()

        selects_by_alias = {
            alias: fragment for fragment, alias in aggregate_query.select
        }

        new_selects = []

        for field in self._fields:
            key = self._sql_alias(field.alias)

            # old field might be directly selected in the base query,
            # in which case we need to alias its expression. If it's
            # not directly in the base, it won't be in the top-level selects
            # list, but will be aliased to the known name in a subquery.
            old_field = selects_by_alias.get(key, key)

            new_alias = self._sql_alias(field.alias)

            if field.function == field.FUNCTION_VALUE:
                group_by.append(old_field)
                new_selects.append((old_field, new_alias))
            elif field.function != field.FUNCTION_VALUE:
                cast = FUNCTION_PARAMETER_CAST.get(field.function, "")
                new_selects.append((f"{field.function}({old_field}{cast})", new_alias))

        # TODO: instead of replacing selects, use sub-query
        aggregate_query.select = new_selects
        aggregate_query.group_by = group_by
        aggregate_query.select_direct_only = True

        sql_query, params, _ = sql.QueryRender(aggregate_query).as_sql(alias=None)

        return sql_query, params

    @cached_property
    def field_ordering(self):
        return list(self.table.fields.all().values_list("alias", flat=True))

    def get_records(self):
        self._summary = defaultdict(int)
        sql_query, params = self.get_sql_and_params()

        with connection.connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(sql_query, params)
            data = cursor.fetchall()

            result = []
            for row in data:
                record = {}
                for field in self._fields:
                    field2 = self.base_table._fields[field.alias]
                    if field.show_output:
                        value = row[self._sql_alias(field.alias)]
                        self._update_summary(field, value)
                        record[field.alias] = field2.parse_value(value)
                result.append(record)

            return result

    def _update_summary(self, field, value):
        # value must to eval to True in order to not break on `None` and also ignore `0`
        if value and field.function in [field.FUNCTION_SUM, field.FUNCTION_COUNT]:
            self._summary[field.alias] += value

    def get_summary(self):
        if not self._summary:  # pragma: no cover
            self.get_records()
        return self._summary
