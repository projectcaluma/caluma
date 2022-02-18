from __future__ import annotations  # self-referencing annotations

from functools import cached_property

from django.db import connection
from psycopg2.extras import DictCursor

from . import simple_table, sql


class PivotTable:
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

    @cached_property
    def _fields(self):
        return list(self.table.fields.all())

    def get_sql_and_params(self):
        """Return a list of records as specified in the given table config."""

        group_by = []
        base_table = simple_table.SimpleTable(self.table.base_table)

        # We replace the selects from the analytics query with
        # the aggregate function calls as required, but leave the
        # rest intact. This way, we won't need to build a subquery
        # around the whole thing and keep it relatively (!) simple
        aggregate_query = base_table.get_query_object()

        selects_by_alias = {
            alias: fragment for fragment, alias in aggregate_query.select
        }

        new_selects = []

        for field in self._fields:
            key = f"analytics_result_{field.data_source}"

            old_field = selects_by_alias[key]
            new_alias = f"analytics_result_{field.alias}"

            if field.function == field.FUNCTION_GROUP:
                group_by.append(old_field)
                new_selects.append((old_field, new_alias))
            else:
                new_selects.append((f"{field.function}({old_field})", new_alias))

        aggregate_query.select = new_selects
        aggregate_query.group_by.extend(group_by)
        aggregate_query.select_direct_only = True

        sql_query, params, _ = sql.QueryRender(aggregate_query).as_sql(alias=None)

        return sql_query, params

    def get_records(self):

        # TODO: this is exactly the same as SimpleTable.get_records(). Can we share code?
        sql_query, params = self.get_sql_and_params()

        with connection.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_query, params)
            data = cursor.fetchall()

            return [
                {
                    # TODO: do we need a parse_value() equivalent here?
                    field.alias: row[f"analytics_result_{field.alias}"]
                    for field in self._fields
                }
                for row in data
            ]

    def _sql_alias(self, user_alias):  # pragma: no cover
        return f"analytics_pivot_{user_alias}"
