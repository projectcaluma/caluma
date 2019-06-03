import pytest


def test_offset_pagination(db, schema_executor, document_factory):
    document_factory(meta={"position": 0})
    document_factory(meta={"position": 1})
    document_factory(meta={"position": 2})
    document_factory(meta={"position": 3})
    document_factory(meta={"position": 4})

    query = """
        query AllDocumentsQuery {
          allDocuments(limit: 2, offset: 2) {
            totalCount
            edges {
              node {
                id
                meta
              }
            }
          }
        }
    """

    result = schema_executor(query)

    assert not result.errors
    assert len(result.data["allDocuments"]["edges"]) == 2
    assert result.data["allDocuments"]["totalCount"] == 2
    assert result.data["allDocuments"]["edges"][0]["node"]["meta"]["position"] == 2
    assert result.data["allDocuments"]["edges"][1]["node"]["meta"]["position"] == 3


@pytest.mark.parametrize(
    "first,last,before,after,has_next,has_previous",
    [
        (1, None, None, None, True, False),
        (None, 1, None, None, False, True),
        (None, None, None, None, False, False),
        (None, None, None, "YXJyYXljb25uZWN0aW9uOjI=", False, True),
        (None, None, "YXJyYXljb25uZWN0aW9uOjI=", None, True, False),
    ],
)
def test_has_next_previous(
    db,
    first,
    last,
    before,
    after,
    has_next,
    has_previous,
    schema_executor,
    document_factory,
):
    document_factory.create_batch(5)

    query = """
        query AllDocumentsQuery ($first: Int, $last: Int, $before: String, $after: String) {
          allDocuments(first: $first, last: $last, before: $before, after: $after) {
            pageInfo {
              hasNextPage
              hasPreviousPage
            }
            edges {
              node {
                id
              }
            }
          }
        }
    """

    inp = {"first": first, "last": last, "before": before, "after": after}

    result = schema_executor(query, variables=inp)

    assert not result.errors
    assert result.data["allDocuments"]["pageInfo"]["hasNextPage"] == has_next
    assert result.data["allDocuments"]["pageInfo"]["hasPreviousPage"] == has_previous
