import pytest
from graphql_relay import offset_to_cursor


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


@pytest.mark.parametrize(
    "after,expected_count",
    [
        (
            offset_to_cursor(4),  # graphene offset starts at 0
            5,
        ),
        (None, 10),
    ],
)
def test_offset_pagination(
    db, schema_executor, question_factory, after, expected_count
):
    question_factory.create_batch(20)

    query = """
        query($after: String, $offset: Int!) {
          allQuestions(after: $after, offset: $offset) {
            totalCount
            edges {
              node {
                id
              }
            }
          }
        }
    """

    result = schema_executor(
        query,
        variable_values={"after": after, "offset": 10},  # input offset starts at 1
    )

    assert not result.errors
    assert len(result.data["allQuestions"]["edges"]) == expected_count


def test_no_default_limit(db, schema_executor, question_factory):
    question_factory.create_batch(120)

    query = """
        query {
          allQuestions {
            totalCount
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
    assert result.data["allQuestions"]["totalCount"] == 120
    assert len(result.data["allQuestions"]["edges"]) == 120


def test_pagination_cursor(db, schema_executor, question_factory):
    question_factory.create_batch(47)

    query = """
        query($after: String) {
          allQuestions(first: 30, after: $after) {
            pageInfo {
              endCursor
            }
            edges {
              cursor
              node {
                id
              }
            }
          }
        }
    """

    cursor = None
    result = schema_executor(query, variable_values={"after": cursor})

    assert not result.errors
    assert len(result.data["allQuestions"]["edges"]) == 30
    cursor = result.data["allQuestions"]["pageInfo"]["endCursor"]

    result2 = schema_executor(query, variable_values={"after": cursor})
    assert len(result2.data["allQuestions"]["edges"]) == 17
