from graphql_relay.connection.arrayconnection import (
    get_offset_with_default,
    offset_to_cursor,
)
from graphql_relay.connection.connectiontypes import Connection, Edge, PageInfo


def connection_from_list(data, args=None, **kwargs):
    """
    Replace graphql_relay.connection.arrayconnection.connection_from_list.

    This can be removed, when (or better if)
    https://github.com/graphql-python/graphql-relay-py/issues/12
    is resolved.

    A simple function that accepts an array and connection arguments, and returns
    a connection object for use in GraphQL. It uses array offsets as pagination,
    so pagination will only work if the array is static.
    """
    _len = len(data)
    return connection_from_list_slice(
        data, args, slice_start=0, list_length=_len, list_slice_length=_len, **kwargs
    )


def connection_from_list_slice(
    list_slice,
    args=None,
    connection_type=None,
    edge_type=None,
    pageinfo_type=None,
    slice_start=0,
    list_length=0,
    list_slice_length=None,
):
    """
    Replace graphql_relay.connection.arrayconnection.connection_from_list_slice.

    This can be removed, when (or better if)
    https://github.com/graphql-python/graphql-relay-py/issues/12
    is resolved.

    Given a slice (subset) of an array, returns a connection object for use in
    GraphQL.
    This function is similar to `connectionFromArray`, but is intended for use
    cases where you know the cardinality of the connection, consider it too large
    to materialize the entire array, and instead wish pass in a slice of the
    total result large enough to cover the range specified in `args`.
    """
    connection_type = connection_type or Connection
    edge_type = edge_type or Edge
    pageinfo_type = pageinfo_type or PageInfo

    args = args or {}

    before = args.get("before")
    after = args.get("after")
    first = args.get("first")
    last = args.get("last")
    if list_slice_length is None:  # pragma: no cover
        list_slice_length = len(list_slice)
    slice_end = slice_start + list_slice_length
    before_offset = get_offset_with_default(before, list_length)
    after_offset = get_offset_with_default(after, -1)

    start_offset = max(slice_start - 1, after_offset, -1) + 1
    end_offset = min(slice_end, before_offset, list_length)
    if isinstance(first, int):
        end_offset = min(end_offset, start_offset + first)
    if isinstance(last, int):
        start_offset = max(start_offset, end_offset - last)

    # If supplied slice is too large, trim it down before mapping over it.
    _slice = list_slice[
        max(start_offset - slice_start, 0) : list_slice_length
        - (slice_end - end_offset)
    ]
    edges = [
        edge_type(node=node, cursor=offset_to_cursor(start_offset + i))
        for i, node in enumerate(_slice)
    ]

    first_edge_cursor = edges[0].cursor if edges else None
    last_edge_cursor = edges[-1].cursor if edges else None

    return connection_type(
        edges=edges,
        page_info=pageinfo_type(
            start_cursor=first_edge_cursor,
            end_cursor=last_edge_cursor,
            has_previous_page=start_offset > 0,
            has_next_page=end_offset < list_length,
        ),
    )
