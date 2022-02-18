import pytest

from caluma.caluma_workflow.models import Case

from ..simple_table import CaseStartingObject, SimpleTable


def test_get_fields(
    db,
    settings,
    snapshot,
    form_and_document,
    info,
    case,
    form_question_factory,
):
    form, document, questions, answers_dict = form_and_document(True, True)
    form_question_factory(
        form=questions["form"].sub_form,
        question__slug="another_question",
        question__type="date",
    )
    form_question_factory(
        form=form,
        question__slug="another_top_question",
        question__type="text",
    )

    # we need a case doc for this to work
    case.document = document
    case.save()

    start = CaseStartingObject(info, disable_visibilities=True)

    # First, see if we only get the depth we want
    fields = start.get_fields(depth=1)

    toplevel_fields = set(
        [
            "id",
            "meta",
            "closed_at",
            "created_at",
            "status",
            "document[top_form]",
        ]
    )

    assert set(fields.keys()) == toplevel_fields

    fields = start.get_fields(depth=10)

    # Now we want alllll the fields
    assert set(fields.keys()) == toplevel_fields.union(
        set(
            [
                "created_at.month",
                "created_at.quarter",
                "created_at.weekday",
                "created_at.year",
                "closed_at.month",
                "closed_at.quarter",
                "closed_at.weekday",
                "closed_at.year",
                "meta.foobar",
                "meta.test-key",
                "document[top_form].form",
                "document[top_form].top_question",
                "document[top_form].another_top_question",
                "document[top_form].form.sub_question",
                "document[top_form].form.another_question",
                "document[top_form].form.another_question.weekday",
                "document[top_form].form.another_question.month",
                "document[top_form].form.another_question.year",
                "document[top_form].form.another_question.quarter",
            ]
        )
    )


@pytest.mark.parametrize("analytics_table__table_type", ["type_extraction"])
def test_extract_form_field_values(
    db,
    settings,
    snapshot,
    form_and_document,
    case,
    form_question_factory,
    analytics_table,
):
    form, document, questions, answers_dict = form_and_document(True, True)
    date_question = form_question_factory(
        form=questions["form"].sub_form,
        question__slug="another_question",
        question__type="date",
    ).question

    form_question_factory(
        form=form,
        question__slug="another_top_question",
        question__type="text",
    )

    date_ans = document.answers.create(question=date_question, date="2021-10-13")

    # we need a case doc for this to work
    case.document = document
    case.save()

    analytics_table.fields.create(
        alias="some_date", data_source="document[top_form].form.another_question"
    )
    analytics_table.fields.create(
        alias="quarter_of_some_date",
        data_source="document[top_form].form.another_question.quarter",
    )

    table = SimpleTable(analytics_table)
    date_ans.refresh_from_db()

    assert table.get_records() == [
        {"some_date": date_ans.date, "quarter_of_some_date": 4}
    ]


@pytest.mark.parametrize("analytics_table__table_type", ["type_extraction"])
def test_workitem_data(
    db,
    settings,
    snapshot,
    info,
    form_and_document,
    case,
    work_item_factory,
    task,
    form_question_factory,
    analytics_table,
):
    form, document, questions, answers_dict = form_and_document(True, True)

    # we need a case doc for this to work
    case.document = document
    case.save()
    Case.objects.all().exclude(pk=case.pk).delete()

    first_wi = work_item_factory(
        case=case,
        task=task,
        created_at="2021-10-10T00:00:00+02:00",
        closed_at="2021-11-10T00:00:00+01:00",
        child_case=None,
    )
    last_wi = work_item_factory(
        case=case,
        task=task,
        created_at="2021-10-15T00:00:00+02:00",
        closed_at="2021-11-20T00:00:00+01:00",
        child_case=None,
    )
    # refresh, so dates are same as freshly read form DB
    first_wi.refresh_from_db()
    last_wi.refresh_from_db()

    # Just checking preconditions...
    assert Case.objects.count() == 1

    start = CaseStartingObject(info, disable_visibilities=True)

    # Checking for presence of the workitem fields
    fields = start.get_fields(depth=3, prefix=[f"workitem[{task.slug},first]"])
    assert len(fields) == 22

    analytics_table.fields.create(
        alias="first_workitem_created",
        data_source=f"workitem[{task.slug},first].created_at",
    )
    analytics_table.fields.create(
        alias="last_workitem_closed",
        data_source=f"workitem[{task.slug},lastclosed].closed_at",
    )
    analytics_table.fields.create(
        alias="case_id",
        data_source="id",
    )

    table = SimpleTable(analytics_table)

    # there are two workitems in our case, but we still expect only one row,
    # as there's only one case. Also, the correct workitems must be selected for
    # the appropriate field.
    analytics_data = table.get_records()
    assert len(analytics_data) == 1
    assert analytics_data == [
        {
            "case_id": case.pk,
            "first_workitem_created": first_wi.created_at,
            "last_workitem_closed": last_wi.closed_at,
        }
    ]


@pytest.mark.parametrize("analytics_table__table_type", ["type_extraction"])
@pytest.mark.parametrize(
    "enable_filter, expect_output", [(True, [0, 1]), (False, [0, 1, 2])]
)
def test_basic_filtering(
    db,
    settings,
    snapshot,
    form_and_document,
    case_factory,
    work_item_factory,
    task,
    form_question_factory,
    analytics_table,
    enable_filter,
    expect_output,
):
    # two case/document combos that we will filter for
    form, document1, questions, answers_dict1 = form_and_document(False, False)
    case1 = case_factory(document=document1)
    form, document2, questions, answers_dict2 = form_and_document(False, False)
    case2 = case_factory(document=document2)

    # a third form/document/case combo that we don't filter for and should
    # therefore not be in the result set
    form, document3, questions, answers_dict3 = form_and_document(False, False)
    case3 = case_factory(document=document3)

    analytics_table.fields.create(
        alias="case_id",
        data_source="id",
    )
    analytics_table.fields.create(
        alias="blablub",
        data_source="document[top_form].top_question",
        filters=[
            answers_dict1["top_question"].value,
            answers_dict2["top_question"].value,
        ]
        if enable_filter
        else [],
    )

    table = SimpleTable(analytics_table)

    # there are two workitems in our case, but we still expect only one row,
    # as there's only one case. Also, the correct workitems must be selected for
    # the appropriate field.
    analytics_data = table.get_records()

    analyzed_output = [
        {
            "case_id": case1.pk,
            "blablub": answers_dict1["top_question"].value,
        },
        {
            "case_id": case2.pk,
            "blablub": answers_dict2["top_question"].value,
        },
        {
            "case_id": case3.pk,
            "blablub": answers_dict3["top_question"].value,
        },
    ]
    expected_data = [analyzed_output[idx] for idx in expect_output]
    assert sorted(analytics_data, key=lambda k: k["case_id"]) == sorted(
        expected_data, key=lambda k: k["case_id"]
    )
