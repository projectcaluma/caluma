from __future__ import annotations  # self-referencing annotations

from functools import cached_property

from django.db import connection
from psycopg2.extras import DictCursor

from . import models, simple_table, sql

FUNCTION_PARAMETER_CAST = {
    "sum": "::float",
    "avg": "::float",
}


class PivotTable:
    class _AnonymousInfo:
        """
        Pseudo GraphQL info object.

        Used for commandline access, so the commandline version
        can also invoke the visibilities.
        """

        context = {}

    def __init__(self, table, info=_AnonymousInfo, is_summary=False):
        self.info = info

        self.table = table
        self.last_query = None
        self.last_query_params = None
        self.base_table = simple_table.SimpleTable(self.table, is_summary=is_summary)
        self.is_summary = is_summary

    @cached_property
    def _fields(self):
        fields = self.table.fields.all()
        if self.is_summary:
            fields = fields.exclude(function=models.AnalyticsField.FUNCTION_VALUE)

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
            key = f"analytics_result_{field.alias}"

            # old field might be directly selected in the base query,
            # in which case we need to alias it's expression. If it's
            # not directly in the base, it won't be in the top-level selects
            # list, but will be aliased to the known name in a subquery.
            old_field = selects_by_alias.get(key, key)

            new_alias = f"analytics_result_{field.alias}"

            if field.function == field.FUNCTION_VALUE:
                group_by.append(old_field)
                new_selects.append((old_field, new_alias))
            else:
                cast = FUNCTION_PARAMETER_CAST.get(field.function, "")
                new_selects.append((f"{field.function}({old_field}{cast})", new_alias))

        aggregate_query.select = new_selects
        aggregate_query.group_by = group_by
        aggregate_query.select_direct_only = True

        sql_query, params, _ = sql.QueryRender(aggregate_query).as_sql(alias=None)

        return sql_query, params

    def get_records(self):
        sql_query, params = self.get_sql_and_params()

        with connection.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_query, params)
            data = cursor.fetchall()

            return [
                {
                    field.alias: field.parse_value(
                        row[f"analytics_result_{field.alias}"]
                    )
                    for field in self.base_table._fields.values()
                    if field.show_output
                }
                for row in data
            ]

    def get_summary(self):
        summary_self = PivotTable(self.table, self.info, is_summary=True)
        summary = summary_self.get_records()
        return summary[0]

    def _sql_alias(self, user_alias):  # pragma: no cover
        return f"analytics_pivot_{user_alias}"
