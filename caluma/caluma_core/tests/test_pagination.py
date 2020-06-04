import pytest


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

    result = schema_executor(query, variable_values=inp)

    assert not result.errors
    assert result.data["allDocuments"]["pageInfo"]["hasNextPage"] == has_next
    assert result.data["allDocuments"]["pageInfo"]["hasPreviousPage"] == has_previous
