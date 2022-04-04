import pytest

from ..models import AnalyticsField


@pytest.mark.parametrize(
    "analytics_table__starting_object", ["cases", "documents", "work_items"]
)
def test_get_fields(
    db, settings, snapshot, form_and_document, info, analytics_cases, analytics_table
):
    form, document, questions, answers_dict = form_and_document(True, True)

    start = analytics_table.get_starting_object(info)
    fields = start.get_fields(depth=10)
    field_info_dict = {
        field: {
            "is_leaf": fieldinfo.is_leaf(),
            "is_value": fieldinfo.is_value(),
            "supported_functions": fieldinfo.supported_functions(),
        }
        for field, fieldinfo in fields.items()
    }

    snapshot.assert_match(field_info_dict)


@pytest.mark.parametrize(
    "analytics_table__starting_object, fields",
    [
        (
            "cases",
            [
                "document[top_form].form.sub_question",
                "document[top_form].top_question",
            ],
        ),
        (
            "documents",
            [
                "created_at.month",
                "form_id",
                "answers[sub_form].sub_question",
            ],
        ),
        (
            "work_items",
            [
                "closed_at",
                "document[top_form].form.sub_question",
                "document[top_form].top_question",
            ],
        ),
    ],
)
def test_extract_values(
    db,
    settings,
    snapshot,
    form_and_document,
    info,
    analytics_cases,
    work_item_factory,
    analytics_table,
    fields,
):
    form, document, questions, answers_dict = form_and_document(True, True)

    for field in fields:
        last_field = field.split(".")[-1]
        analytics_table.fields.create(
            data_source=field,
            alias=last_field,
            function=AnalyticsField.FUNCTION_VALUE,
        )

    if analytics_table.starting_object == "work_items":
        # also create some workitems for our analytics. Don't care too
        # much about being realistic, we just want some work items with
        # documents. So we reuse the documents
        for case in analytics_cases:
            work_item_factory(document=case.document)
    elif analytics_table.starting_object == "documents":
        # only analyze one form - for now
        form_id_field = analytics_table.fields.get(alias="form_id")
        form_id_field.filters = ["top_form"]
        form_id_field.save()

    table = analytics_table.get_analytics(info)

    output = table.get_records()
    output_sorted = sorted(output, key=lambda r: str(r[last_field]))

    snapshot.assert_match(output_sorted)
