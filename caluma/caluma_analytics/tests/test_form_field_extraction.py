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
            "document[*]",
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
                "document[*].another_question",
                "document[*].another_question.month",
                "document[*].another_question.quarter",
                "document[*].another_question.weekday",
                "document[*].another_question.year",
                "document[*].another_top_question",
                "document[*].caluma_form",
                "document[*].caluma_form.name",
                "document[*].caluma_form.name.de",
                "document[*].caluma_form.name.en",
                "document[*].caluma_form.name.fr",
                "document[*].caluma_form.slug",
                "document[*].column",
                "document[*].form",
                "document[*].form.another_question",
                "document[*].form.another_question.month",
                "document[*].form.another_question.quarter",
                "document[*].form.another_question.weekday",
                "document[*].form.another_question.year",
                "document[*].form.caluma_form",
                "document[*].form.caluma_form.name",
                "document[*].form.caluma_form.name.de",
                "document[*].form.caluma_form.name.en",
                "document[*].form.caluma_form.name.fr",
                "document[*].form.caluma_form.slug",
                "document[*].form.sub_question",
                "document[*].sub_question",
                "document[*].top_question",
                "document[top_form].caluma_form",
                "document[top_form].caluma_form.name",
                "document[top_form].caluma_form.name.de",
                "document[top_form].caluma_form.name.en",
                "document[top_form].caluma_form.name.fr",
                "document[top_form].caluma_form.slug",
                "document[top_form].form",
                "document[top_form].top_question",
                "document[top_form].another_top_question",
                "document[top_form].caluma_form.slug",
                "document[top_form].form.sub_question",
                "document[top_form].form.another_question",
                "document[top_form].form.another_question.weekday",
                "document[top_form].form.another_question.month",
                "document[top_form].form.another_question.year",
                "document[top_form].form.another_question.quarter",
                "document[top_form].form.caluma_form",
                "document[top_form].form.caluma_form.name",
                "document[top_form].form.caluma_form.name.de",
                "document[top_form].form.caluma_form.name.en",
                "document[top_form].form.caluma_form.name.fr",
                "document[top_form].form.caluma_form.slug",
            ]
        )
    )


def test_get_fields_for_choice(
    db,
    settings,
    snapshot,
    form_and_document,
    info,
    case,
    form_question_factory,
    question_option_factory,
):
    form, document, *_ = form_and_document(True, True)
    choice_q = form_question_factory(
        form=form,
        question__slug="some_choice",
        question__type="choice",
    ).question
    question_option_factory.create_batch(3, question=choice_q)

    # we need a case doc for this to work
    case.document = document
    case.save()

    start = CaseStartingObject(info, disable_visibilities=True)

    # Choice field should be value and non-leaf, as it
    # has the label as sub-field
    fields = start.get_fields(depth=1, prefix="document[top_form]")
    choice_field = fields["document[top_form].some_choice"]
    assert not choice_field.is_leaf()
    assert choice_field.is_value()

    # Check if choice label fields give correct information
    # about being values / leaves as well
    fields = start.get_fields(depth=2, prefix="document[top_form].some_choice")
    assert set(fields.keys()) == set(
        [
            "document[top_form].some_choice.label",
            "document[top_form].some_choice.label.de",
            "document[top_form].some_choice.label.en",
            "document[top_form].some_choice.label.fr",
        ]
    )

    assert fields["document[top_form].some_choice.label"].is_leaf() is False
    assert fields["document[top_form].some_choice.label"].is_value() is True
    assert fields["document[top_form].some_choice.label.en"].is_leaf() is True
    assert fields["document[top_form].some_choice.label.en"].is_value() is True

    for path, field in fields.items():
        assert ".".join(field.source_path()) == path


@pytest.mark.parametrize("analytics_table__starting_object", ["cases"])
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


@pytest.mark.parametrize("analytics_table__starting_object", ["cases"])
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
    assert len(fields) == 34

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


@pytest.mark.parametrize("analytics_table__starting_object", ["cases"])
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
