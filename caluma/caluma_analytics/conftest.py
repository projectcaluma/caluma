import pytest


@pytest.fixture
def example_analytics(analytics_table, form_and_document, settings):
    settings.META_FIELDS = ["foo"]
    analytics_table.fields.create(data_source="created_at", alias="created_at")
    analytics_table.fields.create(data_source="created_at.quarter", alias="quarter")
    analytics_table.fields.create(data_source="meta.foo", alias="foo")
    analytics_table.fields.create(data_source="status", alias="statuuuuuus")
    analytics_table.fields.create(
        data_source="document[top_form].top_question", alias="from_the_doc"
    )
    return analytics_table


@pytest.fixture
def analytics_cases(form_and_document, case_factory):
    _f, document, _q, _a = form_and_document(use_subform=True)
    for _ in range(3):
        case_factory(meta={"foo": "bar"}, document=document.copy())
