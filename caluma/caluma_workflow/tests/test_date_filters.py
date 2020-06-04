import pytest


@pytest.mark.parametrize(
    "filter,expected_result",
    [
        ([{"createdBefore": "2020-04-21T00:00:00Z"}], [20]),
        ([{"createdBefore": "2020-04-22T00:00:00Z"}], [20, 21]),
        ([{"createdAfter": "2020-04-21T00:00:00Z"}], [21, 22, 23, 24]),
        ([{"createdAfter": "2020-04-22T00:00:00Z"}], [22, 23, 24]),
        # combinations
        (
            [
                {"createdBefore": "2020-04-23T00:00:00Z"},
                {"createdAfter": "2020-04-22T00:00:00Z"},
            ],
            [22],
        ),
        (
            [
                {"createdBefore": "2020-04-24T00:00:00Z"},
                {"createdAfter": "2020-04-21T00:00:00Z"},
            ],
            [21, 22, 23],
        ),
    ],
)
def test_before_after_filters(
    db, case_factory, schema_executor, filter, expected_result
):
    # thanks, auto_now_add!
    cases = case_factory.create_batch(5)
    case_dict = {}
    for day, case in zip(range(20, 25), cases):
        case_dict[day] = case.pk
        case.created_at = f"2020-04-{day} 00:00:00Z"
        case.meta = {"test_created": day}
        case.save()

    query = """
            query Q($filter: [CaseFilterSetType]) {
              allCases(filter: $filter) {
                edges {
                  node {
                    id
                    meta
                  }
                }
              }
            }
        """

    result = schema_executor(query, variable_values={"filter": filter})

    assert not result.errors
    result_info = set(
        case["node"]["meta"]["test_created"]
        for case in result.data["allCases"]["edges"]
    )

    assert result_info == set(expected_result)
