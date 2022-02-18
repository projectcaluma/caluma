import json

import pytest
from django.core.management import call_command

from .. import models


@pytest.mark.parametrize(
    "analytics_table__table_type", [models.AnalyticsTable.TYPE_EXTRACTION]
)
@pytest.mark.parametrize(
    "enable_filter, expect_output", [(True, [0, 1]), (False, [0, 1, 2])]
)
@pytest.mark.parametrize("output_mode", [[], ["--sql"], ["--sqlonly"], ["--json"]])
def test_cmdline_output(
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
    output_mode,
    capsys,
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

    args = [analytics_table.slug] + output_mode

    call_command("run_analytics", *args)

    out, err = capsys.readouterr()

    out = out.replace(str(case1.pk), "case1pk")
    out = out.replace(str(case2.pk), "case2pk")
    out = out.replace(str(case3.pk), "case3pk")

    # This test explicitly disregards ordering
    if output_mode == ["--json"]:
        data = sorted(json.loads(out), key=lambda x: x["blablub"])
    else:
        data = sorted(out.splitlines())

    snapshot.assert_match({"data": data, "stderr": err})


def test_list_tables(db, analytics_table, capsys, snapshot):

    call_command("run_analytics")
    out, err = capsys.readouterr()

    assert analytics_table.slug in out
    snapshot.assert_match(out)
