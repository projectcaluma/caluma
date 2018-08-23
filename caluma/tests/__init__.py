import json

from graphene.utils.str_converters import to_camel_case
from graphql_relay import to_global_id


def extract_serializer_input_fields(serializer_class, instance):
    serializer = serializer_class(instance)

    result = {}
    for key, value in serializer.data.items():
        if isinstance(value, dict):
            value = json.dumps(value)
        result[to_camel_case(key)] = value

    result["clientMutationId"] = "testid"

    return result


def extract_global_id_input_fields(instance):
    global_id = to_global_id(type(instance).__name__, instance.pk)
    return {"id": global_id, "clientMutationId": "testid"}
