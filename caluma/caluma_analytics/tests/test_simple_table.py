import math
import random

import pytest

from caluma.caluma_analytics.models import AnalyticsField
from caluma.caluma_analytics.pivot_table import PivotTable
from caluma.caluma_analytics.simple_table import SimpleTable
from caluma.caluma_form.models import Form, Question


@pytest.mark.parametrize("analytics_table__starting_object", ["cases"])
@pytest.mark.freeze_time("2021-10-10")
def test_run_analytics_direct(db, snapshot, example_analytics, analytics_cases):
    """Test basic analytics run on simple table.

    * Test that we get *some* results
    * Tests date part extraction
    * Test Meta field extraction
    """

    table = SimpleTable(example_analytics)

    result = table.get_records()

    assert len(result) == 10

    snapshot.assert_match(result)


@pytest.mark.parametrize("analytics_table__starting_object", ["cases"])
@pytest.mark.freeze_time("2021-10-10")
@pytest.mark.parametrize("delete_case", [True, False])
@pytest.mark.parametrize("case__meta", [{"foo": "bar"}])
def test_run_analytics_gql(
    db, snapshot, schema_executor, example_analytics, case, delete_case
):
    """Test basic analytics run on simple table.

    * Test that we get *some* results
    * Tests date part extraction
    * Test Meta field extraction
    """
    query = """
        query run ($input: String!) {
          analyticsTable(slug: $input) {
            resultData {
              records {
                edges {
                  node {
                    edges {
                      node {
                        alias
                        value
                      }
                    }
                  }
                }
              }
              summary {
                edges {
                  node {
                    alias
                    value
                  }
                }
              }
            }
          }
        }
    """

    example_analytics.fields.filter(alias="from_the_doc").delete()
    example_analytics.fields.filter(alias="sub_question_sumsumsum").delete()

    if delete_case:
        # Test empty output
        case.delete()

    result = schema_executor(query, variable_values={"input": example_analytics.pk})

    assert not result.errors

    if not delete_case:
        # some explicit sanity checks
        records = result.data["analyticsTable"]["resultData"]["records"]["edges"]
        assert len(records) == 1
        first_row = {
            edge["node"]["alias"]: edge["node"]["value"]
            for edge in records[0]["node"]["edges"]
        }

        assert first_row["quarter"] == str(int(math.ceil(case.created_at.month / 3)))
        assert first_row["foo"] == "bar"

    snapshot.assert_match(result.data)


def test_sql_repeatability(
    db,
    example_analytics,
):
    example_analytics.fields.filter(alias="from_the_doc").delete()
    example_analytics.fields.filter(alias="sub_question_sumsumsum").delete()
    table = SimpleTable(example_analytics)

    sql1, params1 = table.get_sql_and_params()
    sql2, params2 = table.get_sql_and_params()

    assert sql1 == sql2
    assert params1 == params2


@pytest.mark.parametrize(
    "alias",
    [
        "hello-world",
        "with spaces",
        "UpperCase",
        "with punctuation.",
        "with punctuation?",
        "with punctuation!",
        "Lorem ipsum dolor sit amet, consetetur sadipsci",  # will be md5-ed
    ],
)
@pytest.mark.parametrize(
    "table",
    [
        "example_analytics",
        "example_pivot_table",
    ],
)
@pytest.mark.freeze_time("2021-10-10")
def test_unusual_aliases(db, table, analytics_cases, alias, request):
    table_obj = request.getfixturevalue(table)

    some_field = table_obj.fields.get(alias="quarter")
    some_field.alias = alias
    some_field.function = "sum"
    some_field.save()

    table = (
        SimpleTable(table_obj) if table_obj.is_extraction() else PivotTable(table_obj)
    )

    result = table.get_records()

    # We just check that the anlysis run went successful
    # and that the alias is represented in the columns
    assert result
    assert alias in result[0]


@pytest.mark.parametrize("use_lang", [None, "de", "en"])
def test_extract_choice_labels(
    settings,
    db,
    form_question_factory,
    question_option_factory,
    answer_factory,
    example_analytics,
    analytics_cases,
    use_lang,
    form_and_document,
):
    settings.LANGUAGES = [("de", "de"), ("en", "en")]

    # We need a form with a choice question ...
    form, *_ = form_and_document(False, False)
    choice_q = form_question_factory(form=form, question__type="choice").question
    options = question_option_factory.create_batch(4, question=choice_q)

    # ... as well as some cases with corresponding answers in their docs
    for case in analytics_cases:
        answer_factory(
            question=choice_q,
            document=case.document,
            value=random.choice(options).option.slug,
        )

        # just checking assumptions..
        assert case.document.form_id == form.pk

    # we're only interested in seeing the choice field work here
    example_analytics.fields.all().delete()
    lang_suffix = f".{use_lang}" if use_lang else ""
    example_analytics.fields.create(
        data_source=f"document[top_form].{choice_q.slug}",
        alias="choice_value",
    )
    example_analytics.fields.create(
        data_source=f"document[top_form].{choice_q.slug}.label{lang_suffix}",
        alias="choice_label",
    )

    # Define valid outputs for label and value (slug)
    lang = use_lang if use_lang else settings.LANGUAGE_CODE
    valid_options = {opt.slug: opt.label[lang] for opt in choice_q.options.all()}

    # Run the analysis
    table = SimpleTable(example_analytics)
    result = table.get_records()

    choice_count = 0
    assert len(result)
    for row in result:
        if row["choice_value"]:
            choice_count += 1
            assert row["choice_value"] in valid_options
            assert row["choice_label"] == valid_options[row["choice_value"]]
    assert choice_count >= len(analytics_cases)


@pytest.mark.parametrize(
    "analytics_table__starting_object, data_source",
    [
        ("cases", "document[*].caluma_form.name"),
        ("documents", "caluma_form.name"),
    ],
)
def test_form_info_field_cases(db, analytics_table, analytics_cases, data_source):
    valid_form_names = [
        str(n) for n in Form.objects.all().values_list("name", flat=True)
    ]

    analytics_table.fields.create(
        alias="the_thing",
        data_source=data_source,
        function=AnalyticsField.FUNCTION_VALUE,
    )

    table = SimpleTable(analytics_table)

    records = table.get_records()
    assert records
    for record in records:
        assert record["the_thing"] in valid_form_names


@pytest.mark.parametrize("analytics_table__starting_object", ["work_items"])
def test_subcase(
    db,
    workflow_factory,
    case_factory,
    work_item_factory,
    form_question_factory,
    answer_factory,
    analytics_table,
):
    # parent workflow & case
    workflow = workflow_factory()
    form_question = form_question_factory(
        question__type=Question.TYPE_TEXT,
        question__slug="main-form-q",
        form__slug="main-form",
    )
    main_answer = answer_factory(
        question=form_question.question,
        document__form=form_question.form,
    )
    case = case_factory(workflow=workflow, document=main_answer.document)

    # sub workflow & child case
    sub_workflow = workflow_factory()
    child_case = case_factory(workflow=sub_workflow, family=case)
    child_form_question = form_question_factory(
        question__type=Question.TYPE_TEXT,
        question__slug="sub-case-form-q",
        form__slug="sub-case-form",
    )
    child_answer = answer_factory(
        question=child_form_question.question,
        document__form=child_form_question.form,
    )
    work_item_factory(case=child_case, document=child_answer.document)

    # access value from parent case document
    analytics_table.fields.create(
        alias="main-form-q",
        data_source="case.family.document[main-form].main-form-q",
        function=AnalyticsField.FUNCTION_VALUE,
    )

    # access value from child case document
    analytics_table.fields.create(
        alias="sub-case-form-q",
        data_source="document[sub-case-form].sub-case-form-q",
        function=AnalyticsField.FUNCTION_VALUE,
    )

    table = SimpleTable(analytics_table)

    records = table.get_records()
    assert records == [
        {"sub-case-form-q": child_answer.value, "main-form-q": main_answer.value}
    ]
