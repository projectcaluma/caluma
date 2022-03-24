from graphql_relay import from_global_id

_valid_types = set()


def extract_global_id(id):
    """
    Extract id from global id throwing away type.

    In case it is not a base64 encoded value it will return id as is.
    This way it can be used as input type by simply defining id without its specific type.
    """
    if not _valid_types:
        # Lazy import due to circular dependency
        from caluma import schema
        from caluma.caluma_core import types

        all_types_dict = {
            **vars(schema.workflow_schema),
            **vars(schema.form_schema),
            **vars(schema.form_historical_schema),
            **vars(schema.analytics_schema),
        }
        all_types = [
            typename
            for typename, gql_type in all_types_dict.items()
            if isinstance(gql_type, type) and issubclass(gql_type, types.Node)
        ]

        _valid_types.update(all_types)

    gql_type, result = from_global_id(id)

    # `from_global_id` might return all kinds of valid strings that we can't
    # interpret as global id which is why we only return the result if it's not
    # empty and the type is in our known types
    if result and gql_type in _valid_types:
        return result

    return id
