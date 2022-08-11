import pytest

from caluma.caluma_workflow import models as workflow_models

from . import models


@pytest.fixture
def example_analytics(analytics_table, settings):
    analytics_table.starting_object = "cases"
    analytics_table.save()

    settings.META_FIELDS = ["foo"]

    analytics_table.fields.create(
        data_source="created_at",
        function=models.AnalyticsField.FUNCTION_VALUE,
        alias="created_at",
    )
    analytics_table.fields.create(
        data_source="created_at.quarter",
        function=models.AnalyticsField.FUNCTION_VALUE,
        alias="quarter",
    )
    analytics_table.fields.create(
        data_source="meta.foo",
        function=models.AnalyticsField.FUNCTION_VALUE,
        alias="foo",
    )
    analytics_table.fields.create(
        data_source="status",
        function=models.AnalyticsField.FUNCTION_VALUE,
        alias="statuuuuuus",
    )
    analytics_table.fields.create(
        data_source="document[top_form].top_question",
        function=models.AnalyticsField.FUNCTION_VALUE,
        alias="from_the_doc",
    )
    analytics_table.fields.create(
        data_source="document[top_form].form.sub_question",
        function=models.AnalyticsField.FUNCTION_VALUE,
        alias="sub_question_sumsumsum",
    )
    return analytics_table


@pytest.fixture
def analytics_cases(form_and_document, case_factory, set_date, work_item_factory):
    """Create a number of cases with documents to be used in testing.

    There are multiple cases with differing statuses and differing
    created_at values:
        * 3x RUNNING, created_at ranging from 2022-02-01 to 2022-01-03
        * 1x COMPLETED, created_at 2022-02-04
        * 1x SUSPENDED, created_at 2022-02-05
    """
    statuses = [
        # multiple cases with same status to test aggregates
        workflow_models.Case.STATUS_RUNNING,  # created_at 2022-02-01
        workflow_models.Case.STATUS_RUNNING,  # created_at 2022-02-02
        workflow_models.Case.STATUS_RUNNING,  # created_at 2022-02-03
        workflow_models.Case.STATUS_COMPLETED,  # created_at 2022-02-04
        workflow_models.Case.STATUS_SUSPENDED,  # created_at 2022-02-05
    ]

    # create each case with another modified_at date

    def _makecase(date, **kwargs):
        with set_date(date):
            _f, document, _q, _a = form_and_document(use_subform=True)
            case = case_factory(
                meta={"foo": "bar"},
                document=document,
                **kwargs,
            )
            work_item_factory(document=document.copy(), case=case)
        return case

    return [
        _makecase(f"2022-02-{day:02}", status=status)
        for day, status in enumerate(statuses, start=1)
    ]


@pytest.fixture
def example_pivot_table(example_analytics):

    status_field = example_analytics.fields.get(alias="statuuuuuus")

    status_field.function = models.AnalyticsField.FUNCTION_VALUE
    status_field.alias = "status"
    status_field.save()

    created_field = example_analytics.fields.get(alias="created_at")
    created_field.function = models.AnalyticsField.FUNCTION_MAX
    created_field.alias = "last_created"
    created_field.save()

    quarter_field = example_analytics.fields.get(alias="quarter")
    quarter_field.function = models.AnalyticsField.FUNCTION_MAX
    quarter_field.save()

    sub_q_field = example_analytics.fields.get(alias="sub_question_sumsumsum")
    sub_q_field.function = models.AnalyticsField.FUNCTION_SUM
    sub_q_field.alias = "sub_question_sumsumsum"
    sub_q_field.save()

    example_analytics.fields.all().exclude(
        pk__in=[status_field.pk, created_field.pk, quarter_field.pk, sub_q_field.pk]
    ).delete()

    return example_analytics
