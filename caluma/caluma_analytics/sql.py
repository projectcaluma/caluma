from __future__ import annotations  # self-referencing annotations

import hashlib
import textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from uuid import uuid4

from django.db import connection
from django.utils.text import slugify


def _make_name(value, name_hint=None):
    prefix = name_hint if name_hint else "p"
    length = 5 if name_hint else 12

    suffix = hashlib.md5(str(value).encode("utf-8")).hexdigest()
    return f"{prefix}_{suffix[:length]}"


@dataclass
class Query:
    """Represent an SQL query (might be a subquery).

    Note: The `from` specification might in turn again
    reference another Query object, thus building a subquery
    structure.
    """

    from_: Union[str, Query]
    distinct_on: Optional[str] = field(default=None)
    select: List[Tuple(str, str)] = field(default_factory=list)  # expression -> alias
    outer_ref: Optional[Tuple(str, str)] = field(
        default=None
    )  # Pair of outer identifier, inner identifier. Used for JOINing

    joins: List[Tuple(Union[str, Query], str)] = field(
        default_factory=list
    )  # table/subquery, join expr

    filters: List[str] = field(default_factory=list)
    order_by: List[str] = field(default_factory=list)
    limit: Optional[int] = field(default=None)
    params: Dict[str, str] = field(default_factory=dict)
    group_by: List[str] = field(default_factory=list)
    with_queries: Dict[str, str] = field(
        default_factory=dict
    )  # with_queries are CTEs, used for referencing visibility-filtered tables

    is_plain_cte: bool = field(default=False)
    select_direct_only: bool = field(default=False)

    def makeparam(self, value, name_hint=None):
        """Return a parameter name for the given value.

        The parameter's value is automatically registered and
        can then be used in the generated SQL.

        If you pass a name_hint, it is used as a prefix
        to better identify the params when debugging the query
        """
        identifier = _make_name(value, name_hint)
        self.params[identifier] = value
        return f"%({identifier})s"

    def outer_alias(self):
        """Alias of the table / subquery, as it is referred to from *outside*.

        Used by outer queries to know how to alias our result expression.
        """

        if isinstance(self.from_, str):
            return self.from_

        subname_data = f"""
            {self.order_by}
            {self.filters}
        """

        # return f"sub_{self.from_.outer_alias()}_{ob}"
        return _make_name(subname_data, self.from_.outer_alias())

    def self_alias(self):
        """Alias of the table / subquery, as it is referred to from within.

        This shall be used for fully-qualified references to fields within
        this query.
        """
        if isinstance(self.from_, str):
            # Only happens if the base table is directly referenced,
            # instead of a subquery (from visibility/django QS).
            return self.from_  # pragma: no cover
        return self.from_.outer_alias()

    def add_field_filter(self, alias, filter_values):
        """Apply the given filters to this field.

        Filters are a list of strings (or numbers), and the field must be
        equal to one of them for the row to end up in the result set.

        Note: No filter (filters=None, or filters=[]) means no restriction.
        As it doesn't really make sense to remove all values (and thus all rows)
        from the resulting data, we treat both as "don't filter" in this case
        """
        if not filter_values:
            return

        filters_sql = ", ".join(
            [self.makeparam(val, f"flt_{alias}") for val in filter_values]
        )
        self.filters.append(f"{alias} IN ({filters_sql})")

    @classmethod
    def from_queryset(cls, queryset):
        """Take a Django queryset and represent it as a Query object.

        We will use this via CTE (WITH) statement to read data respecting
        the visibility rules as defined in Caluma.
        """

        # The queryset may "SELECT" columns (especially from JOINs) that
        # we're not interested in, as we're JOINing our stuff by ourselves.
        # To avoid ambiguity, we select ONLY what's in the main model's
        # field list
        q = connection.ops.quote_name
        field_list = ",  \n".join(
            [
                q(queryset.model._meta.db_table)
                + "."
                + q(field.db_column or field.attname)
                for field in queryset.model._meta.concrete_fields
            ]
        )

        # Unfortunately, queryset.query.sql_with_params() seems to
        # ignore queryset.only() specification, so we must do it ourselves.
        # Ugly AF, but don't see how else to do it for now...
        sql, params = queryset.query.sql_with_params()
        select, from_part = sql.split("FROM", 1)

        wrapped_sql = f"""SELECT {field_list}\nFROM\n      {from_part} -- qs ref\n"""

        name = _make_name(value=wrapped_sql, name_hint=queryset.model.__name__.lower())
        self = cls(from_=name, is_plain_cte=True)

        # Django does positional parameters, we do named params. Convert them
        named_params = [self.makeparam(param) for param in params]
        final_sql = wrapped_sql % named_params

        self.with_queries[name] = final_sql

        return self


@dataclass
class Field:
    identifier: str
    alias: Optional[str] = field(default=None)
    parent: Optional[Field] = field(default=None)
    filter_values: Optional[List[str]] = field(default=None)
    answer_value_mode: bool = field(default=False)
    _activated_query: Optional[Query] = field(default=None)

    def path_from_root(self):
        path = []
        obj = self
        while obj:
            path.append(obj)
            obj = obj.parent
        return list(reversed(path))

    def _alias(self):
        if not self.alias:  # pragma: todo cover
            self.alias = slugify(self.identifier + "_" + str(uuid4())[:5]).replace(
                "-", "_"
            )
        return self.alias


class NOOPField(Field):
    def annotate(self, query: Query):
        return query


@dataclass
class AttrField(Field):
    def annotate(self, query: Query):
        if self._activated_query:  # pragma: no cover
            assert query is self._activated_query
            return query

        self._activated_query = query
        query.select.append((self.expr(query), self._alias()))
        return query

    def expr(self, query):
        # TODO: should the table alias be prefixed in all field expr()s?
        alias = query.self_alias()
        if self.answer_value_mode:
            # Caluma form answers are in a JSON field named "value", from where
            # we need to extract the actual value, otherwise, for strings, we
            # would get the quoted version back
            extractor_op = "#>>'{}'"  # noqa
            return f"({alias}.{self.identifier} {extractor_op})"
        return f"{alias}.{self.identifier}"


@dataclass
class DateExprField(AttrField):
    extract_part: Optional[str] = field(default=None)

    def expr(self, query):
        q_id = connection.ops.quote_name(self.identifier)
        return f"EXTRACT({self.extract_part} FROM {q_id})"


@dataclass
class JSONExtractorField(AttrField):
    json_key: Optional[str] = field(default=None)

    def expr(self, query):
        key_param = query.makeparam(self.json_key)
        q_id = connection.ops.quote_name(self.identifier)
        self_alias = query.self_alias()
        # Extract text from JSON field, so that it comes from the DB
        # as actual text
        extractor_op = "#>>'{}'"  # noqa
        return f"""(({self_alias}.{q_id} -> {key_param}) {extractor_op})"""


@dataclass
class JoinField(Field):
    table: Optional[Union[str, Query]] = field(default=None)
    filters: List[str] = field(default_factory=list)
    order_by: List[str] = field(default_factory=list)
    outer_ref: Optional[Tuple[str, str]] = field(
        default=None
    )  # name_in_outer -> name_in_inner

    def annotate(self, query: Query):
        if self._activated_query:  # pragma: no cover (safeguard)
            return self._activated_query

        self._activated_query = Query(
            from_=self.table,
            # distinct_on is the inner part of the outer_ref
            distinct_on=self.outer_ref[1],
            filters=self.filters,
            outer_ref=self.outer_ref,
            order_by=self.order_by,
            # limit=1,
        )

        outer_ref, inner_ref = self.outer_ref

        query.joins.append(
            (
                self._activated_query,
                f'{query.self_alias()}.{outer_ref} = "{self._activated_query.outer_alias()}".{inner_ref}',
            )
        )
        return self._activated_query


class QueryRender:
    """Render a Query structure into actual SQL.

    The Renderer builds an SQL query, which might consist of multiple
    subqueries, and common table expressions (CTE; "WITH" statements).
    """

    def __init__(self, query: Query, is_subquery=False, indent: int = 0):
        self._indent = indent
        self.query = query
        self.collected_params = {}
        self.with_queries = {}
        self.is_subquery = is_subquery

    def as_sql(self, alias):
        """Return a two-tuple: An SQL statement, and a dict of parameters.

        The parameters should then be passed on to the DB driver, which will
        interpret them accordingly.
        """
        self.collected_params = self.query.params.copy()
        self.with_queries = self.query.with_queries.copy()

        field_list = self._field_list()
        if not field_list and self.query.is_plain_cte:
            return self.query.from_, {}, alias

        selects = f"SELECT {self._distinct_on()}\n       {field_list}"
        from_list = f"FROM {self._from_list()}"
        if self.is_subquery:
            sql = "\n".join(
                [
                    selects,
                    from_list,
                    self._where_list(),
                    self._order_by(),
                    self._group_by(),
                    self._limits(),
                ]
            )
        else:
            # We're the outermost query. Wrap the whole thing in one more level of
            # subquery, so we can filter on the aliases instead of expressions.
            # This is theoretically only required if we have expressions on the
            # outermost table, but for convenience, we do it always.
            inner_sql = "\n".join(
                [selects, from_list, self._order_by(), self._group_by(), self._limits()]
            )
            inner_name = _make_name(inner_sql, "analytics")
            sql = f"SELECT * FROM ({inner_sql}) AS {inner_name}\n{self._where_list()}"

        if self.with_queries and not self.is_subquery:
            # CTEs are only built if we're the outermost query, and
            # we do have CTEs defined
            sql = f"WITH\n{self._with_sql()}\n{sql}"

        return (
            textwrap.indent(sql, prefix=" " * self._indent),
            self.collected_params,
            alias,
        )

    def _with_sql(self):
        with_pairs = [
            textwrap.indent(f"{name} AS ({query})", prefix=" " * (self._indent + 4))
            for name, query in self.with_queries.items()
        ]
        return ",\n".join(with_pairs)

    def _distinct_on(self):
        # DISTINCT ON(foo) only takes the first "foo" row. We use this
        # for example when selecting one sub-item per main table, where
        # multiple might exist (such as the first workitem on a case)
        if self.query.distinct_on:
            return f"DISTINCT ON ({self.query.distinct_on})"
        return ""

    def _order_by(self):
        order_list = []
        if self.query.distinct_on:
            order_list.append(self.query.distinct_on)
        if self.query.order_by:
            # TODO: make parameterizable
            order_list.extend(self.query.order_by)

        if order_list:
            order_sql = ",\n       ".join(order_list)
            return f"ORDER BY {order_sql}"
        return ""

    def _group_by(self):
        if self.query.group_by:
            group_sql = ",\n       ".join(self.query.group_by)
            return f"GROUP BY {group_sql}"
        return ""

    def _limits(self):
        # TODO: Do we still need this? We're doing the same thing now
        # using (DISTINCT ON)
        if self.query.limit:  # pragma: no cover
            return f"LIMIT {self.query.limit}"
        return ""

    def _where_list(self):
        if self.query.filters:
            # TODO: make parameterizable
            filter_sql = " AND\n       ".join(self.query.filters)
            return f"WHERE {filter_sql}"
        return ""

    def _field_list(self):
        # we always need to select everything, even from subqueries
        fields = [
            # First, the direct fields
            f'''{expr} AS "{alias}"'''
            for expr, alias in self.query.select
        ]
        if self.query.outer_ref:
            _, inner = self.query.outer_ref
            fields.append(f'"{inner}"')

        # The subquery fields are already aliased, so no need
        # to re-alias them
        def _collect(q):
            for _, alias in q.select:
                yield f'"{alias}"'
            for sub_q, _ in q.joins:
                yield from _collect(sub_q)

        # Normally, we take all the "selects" from the inner queries and
        # pass them further on. However in aggregate queries, this is not
        # desired, as any unused field will lead to an SQL error (fields
        # MUST be used in aggregates or group by, which may not be desired).
        # Thus we allow the query to specify "select direct only", which means
        # we do not pass on any selected fields from inner queries / joins
        # as we usually would.
        if not self.query.select_direct_only:
            for join, _ in self.query.joins:
                fields.extend(_collect(join))

        return ",\n       ".join(fields)

    def _join_source(self, from_spec):
        """Return a 2-tuple to join the given table/subquery.

        The tuple consists of:
        * subquery/table
        * alias
        """
        if isinstance(from_spec, str):
            # by defintion, only "our own" table can be passed as string.
            # subqueries MUST be query objects
            # Only happens if the base table is directly referenced,
            # instead of a subquery (from visibility/django QS).
            return (from_spec, {}, self.query.outer_alias())  # pragma: no cover

        render = QueryRender(from_spec, indent=self._indent + 4, is_subquery=True)

        sql, params, alias = render.as_sql(from_spec.outer_alias())

        # Take any CTEs from the subquery and apply them to "us"
        self.with_queries.update(render.with_queries)

        return sql, params, alias

    def _from_list(self):

        from_sql, from_params, from_alias = self._join_source(self.query.from_)
        self.collected_params.update(from_params)
        self.with_queries.update(self.query.with_queries)

        sources = [(from_sql, from_alias, "")]

        for tbl, cond in self.query.joins:
            subquery, subparams, alias = self._join_source(tbl)
            self.collected_params.update(subparams)
            if isinstance(tbl, Query):
                self.with_queries.update(tbl.with_queries)

            sources.append(
                (f"LEFT JOIN (\n{subquery}\n)", alias, f"ON ({cond})" if cond else "")
            )

        return "\n".join([f'{tbl} AS "{alias}" {cond}' for tbl, alias, cond in sources])
