import pytest

from ...caluma_core.relay import extract_global_id


@pytest.mark.parametrize(
    "lookup,search,expect",
    [
        (None, "bar", ["exact"]),
        ("EXACT", "bar", ["exact"]),
        ("STARTSWITH", "bar", ["exact", "starts"]),
        ("CONTAINS", "bar", ["contains", "starts", "exact"]),
        ("ICONTAINS", "bar", ["icontains", "contains", "starts", "exact"]),
        (None, True, ["bool"]),
        (None, 123, ["int"]),
        (None, 123.456, ["float"]),
    ],
)
def test_meta_value_filter(
    db, schema_executor, document_factory, lookup, search, expect
):
    docs = {
        "nope": document_factory(meta={"foo": "does not match"}),
        "exact": document_factory(meta={"foo": "bar"}),
        "starts": document_factory(meta={"foo": "bar is what it starts with"}),
        "contains": document_factory(meta={"foo": "contains a bar somewhere"}),
        "icontains": document_factory(meta={"foo": "contains a Bar somewhere"}),
        "bool": document_factory(meta={"foo": True}),
        "int": document_factory(meta={"foo": 123}),
        "float": document_factory(meta={"foo": 123.456}),
    }

    query = """
        query AllDocumentsQuery($filter: [JSONValueFilterType]) {
          allDocuments(metaValue: $filter) {
            edges {
              node {
                id
              }
            }
          }
        }
    """

    variables = {"filter": [{"key": "foo", "value": search}]}
    if lookup:
        variables["filter"][0]["lookup"] = lookup

    result = schema_executor(query, variable_values=variables)

    assert not result.errors

    expected_ids = [str(docs[exp].id) for exp in expect]

    received_ids = [
        extract_global_id(entry["node"]["id"])
        for entry in result.data["allDocuments"]["edges"]
    ]

    assert sorted(received_ids) == sorted(expected_ids)
