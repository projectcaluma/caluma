from ..relay import extract_global_id


def test_inversible_with_vars(db, schema_executor, document_factory):
    nope, found, excluded = (
        document_factory(meta={}),
        document_factory(meta={"foo": "bar"}),
        document_factory(meta={"foo": "bar", "blah": "blub"}),
    )

    variables = {
        "filter": [
            {"metaValue": [{"key": "foo", "value": "bar"}]},
            {"metaValue": [{"key": "blah", "value": "blub"}], "invert": True},
        ]
    }

    query = """
        query AllDocumentsQuery($filter: [DocumentFilterSetType]) {
          allDocuments(filter: $filter) {
            edges {
              node {
                id
              }
            }
          }
        }
    """

    result = schema_executor(query, variable_values=variables)
    assert not result.errors

    result_ids = [
        extract_global_id(n["node"]["id"]) for n in result.data["allDocuments"]["edges"]
    ]

    assert str(nope.pk) not in result_ids
    assert str(found.pk) in result_ids
    assert str(excluded.pk) not in result_ids


def test_inversible_inline(db, schema_executor, document_factory):
    nope, found, excluded = (
        document_factory(meta={}),
        document_factory(meta={"foo": "bar"}),
        document_factory(meta={"foo": "bar", "blah": "blub"}),
    )
    query = """
        query {
          allDocuments(filter: [
            {metaValue: [{key: "foo", value: "bar"}]},
            {metaValue: [{key: "blah", value: "blub"}], invert: true},
          ]) {
            edges {
              node {
                id
              }
            }
          }
        }
    """

    result = schema_executor(query)
    assert not result.errors

    result_ids = [
        extract_global_id(n["node"]["id"]) for n in result.data["allDocuments"]["edges"]
    ]

    assert str(nope.pk) not in result_ids
    assert str(found.pk) in result_ids
    assert str(excluded.pk) not in result_ids
