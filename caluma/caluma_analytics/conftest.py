import pytest

from caluma.caluma_workflow import models as workflow_models

from . import models


@pytest.fixture
def example_analytics(analytics_table, form_and_document, settings):
    settings.META_FIELDS = ["foo"]
    analytics_table.table_type = models.AnalyticsTable.TYPE_EXTRACTION

    analytics_table.fields.create(data_source="created_at", alias="created_at")
    analytics_table.fields.create(data_source="created_at.quarter", alias="quarter")
    analytics_table.fields.create(data_source="meta.foo", alias="foo")
    analytics_table.fields.create(data_source="status", alias="statuuuuuus")
    analytics_table.fields.create(
        data_source="document[top_form].top_question", alias="from_the_doc"
    )
    return analytics_table


@pytest.fixture
def analytics_cases(form_and_document, case_factory, at_date):
    """Create a number of cases with documents to be used in testing.

    There are multiple cases with differing statuses and differing
    created_at values:
        * 3x RUNNING, created_at ranging from 2022-02-01 to 2022-01-03
        * 1x COMPLETED, created_at 2022-02-04
        * 1x SUSPENDED, created_at 2022-02-05
    """
    _f, document, _q, _a = form_and_document(use_subform=True)
    statuses = [
        # multiple cases with same status to test aggregates
        workflow_models.Case.STATUS_RUNNING,  # created_at 2022-02-01
        workflow_models.Case.STATUS_RUNNING,  # created_at 2022-02-02
        workflow_models.Case.STATUS_RUNNING,  # created_at 2022-02-03
        workflow_models.Case.STATUS_COMPLETED,  # created_at 2022-02-04
        workflow_models.Case.STATUS_SUSPENDED,  # created_at 2022-02-05
    ]

    # create each case with another modified_at date

    return [
        # use at_date to create the cases at the correct date.
        at_date(
            f"2022-02-{day:02}",
            lambda: case_factory(
                meta={"foo": "bar"},
                status=status,
                document=document.copy(),
            ),
        )
        for day, status in enumerate(statuses, start=1)
    ]


@pytest.fixture
def example_pivot_table(example_analytics, analytics_table_factory):
    pivot_table = analytics_table_factory(
        table_type=models.AnalyticsTable.TYPE_PIVOT, base_table=example_analytics
    )

    pivot_table.fields.create(
        alias="status",
        data_source="statuuuuuus",
        function=models.AnalyticsField.FUNCTION_GROUP,
    )

    pivot_table.fields.create(
        alias="last_created",
        data_source="created_at",
        function=models.AnalyticsField.FUNCTION_MAX,
    )
    return pivot_table
