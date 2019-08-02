import pytest

from ...core.relay import extract_global_id


@pytest.mark.parametrize(
    "lookup,expect",
    [
        (None, ["exact"]),
        ("EXACT", ["exact"]),
        ("STARTSWITH", ["exact", "starts"]),
        ("CONTAINS", ["contains", "starts", "exact"]),
        ("ICONTAINS", ["icontains", "contains", "starts", "exact"]),
    ],
)
def test_meta_value_filter(db, schema_executor, document_factory, lookup, expect):
    docs = {
        "nope": document_factory(meta={"foo": "does not match"}),
        "exact": document_factory(meta={"foo": "bar"}),
        "starts": document_factory(meta={"foo": "bar is what it starts with"}),
        "contains": document_factory(meta={"foo": "contains a bar somewhere"}),
        "icontains": document_factory(meta={"foo": "contains a Bar somewhere"}),
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

    variables = {"filter": [{"key": "foo", "value": "bar"}]}
    if lookup:
        variables["filter"][0]["lookup"] = lookup

    result = schema_executor(query, variables=variables)

    assert not result.errors

    expected_ids = [str(docs[exp].id) for exp in expect]

    received_ids = [
        extract_global_id(entry["node"]["id"])
        for entry in result.data["allDocuments"]["edges"]
    ]

    assert sorted(received_ids) == sorted(expected_ids)
