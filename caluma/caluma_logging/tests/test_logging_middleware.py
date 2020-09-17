import pytest
from django.urls import reverse

from .. import models


@pytest.mark.parametrize(
    "query,variables,operation,operation_name,selection,status_code",
    [
        (
            """
            query foo {
              allCases {
                edges {
                  node {
                    id
            }}}}
            """,
            "",
            "query",
            "foo",
            "allCases",
            200,
        ),
        (
            """
            query {
              allCases {
                edges {
                  node {
                    id
            }}}}
            """,
            "",
            "query",
            None,
            "allCases",
            200,
        ),
        (
            """
            query {
              foo {
                bar
            }}
            """,
            "",
            "query",
            None,
            "foo",
            400,
        ),
        (
            """
            mutation SaveTextQuestion($input: SaveTextQuestionInput!) {
              saveTextQuestion(input: $input) {
                question {
                  id
                  }
                }
            }
            """,
            {"input": {"slug": "some-text-question", "label": "some text question"}},
            "mutation",
            "SaveTextQuestion",
            "saveTextQuestion",
            200,
        ),
        (
            """
            {
            }""",
            "",
            "",
            None,
            None,
            400,
        ),
    ],
)
def test_access_log(
    db,
    snapshot,
    client,
    schema_executor,
    query,
    variables,
    operation,
    operation_name,
    selection,
    status_code,
):
    url = reverse("graphql")
    res = schema_executor(query, variable_values=variables)

    result = client.post(
        url, {"query": query, "variables": variables}, content_type="application/json"
    )

    # schema executor and actual api call should get both success / errors
    assert (
        result.status_code < 400
        and not res.errors
        or result.status_code >= 400
        and res.errors
    )

    assert models.AccessLog.objects.all().count() == 1
    log_entry = models.AccessLog.objects.get()

    assert log_entry.query == query
    assert log_entry.variables == variables
    assert log_entry.operation_name == operation_name
    assert log_entry.operation == operation
    assert log_entry.selection == selection
    assert log_entry.status_code == status_code == result.status_code
