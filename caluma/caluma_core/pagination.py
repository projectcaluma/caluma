from graphql_relay import (
    Connection,
    Edge,
    PageInfo,
    get_offset_with_default,
    offset_to_cursor,
)


def connection_from_array(
    data,
    args=None,
    connection_type=Connection,
    edge_type=Edge,
    page_info_type=PageInfo,
):
    """
    Replace graphql_relay.connection_from_array.

    This can be removed, when (or better if)
    https://github.com/graphql-python/graphql-relay-py/issues/12
    is resolved.

    A simple function that accepts an array and connection arguments, and returns
    a connection object for use in GraphQL. It uses array offsets as pagination,
    so pagination will only work if the array is static.
    """
    return connection_from_array_slice(
        data,
        args,
        slice_start=0,
        array_length=len(data),
        connection_type=connection_type,
        edge_type=edge_type,
        page_info_type=page_info_type,
    )


def connection_from_array_slice(
    array_slice,
    args=None,
    slice_start=0,
    array_length=None,
    array_slice_length=None,
    connection_type=Connection,
    edge_type=Edge,
    page_info_type=PageInfo,
):
    """
    Replace graphql_relay.connection_from_array_slice.

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
    args = args or {}
    before = args.get("before")
    after = args.get("after")
    first = args.get("first")
    last = args.get("last")
    if array_slice_length is None:  # pragma: no cover
        array_slice_length = len(array_slice)
    slice_end = slice_start + array_slice_length
    before_offset = get_offset_with_default(before, array_length)
    after_offset = get_offset_with_default(after, -1)

    start_offset = max(slice_start - 1, after_offset, -1) + 1
    end_offset = min(slice_end, before_offset, array_length)
    if isinstance(first, int):
        end_offset = min(end_offset, start_offset + first)
    if isinstance(last, int):
        start_offset = max(start_offset, end_offset - last)

    # If supplied slice is too large, trim it down before mapping over it.
    _slice = array_slice[
        max(start_offset - slice_start, 0) : array_slice_length
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
        page_info=page_info_type(
            start_cursor=first_edge_cursor,
            end_cursor=last_edge_cursor,
            has_previous_page=start_offset > 0,
            has_next_page=end_offset < array_length,
        ),
    )
