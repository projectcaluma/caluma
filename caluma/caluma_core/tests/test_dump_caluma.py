import json
from tempfile import NamedTemporaryFile

import pytest
from django.core.management import CommandError, call_command

from ..management.commands.dump_caluma_config import get_form_filters

FORM_MODELS = get_form_filters([]).keys()


def sort_dump(dump):
    return sorted(json.loads(dump), key=lambda x: x["pk"])


def test_dump_caluma_config(db, form_and_document, snapshot, form_factory):
    temp_file = NamedTemporaryFile()

    # first: no content
    call_command(
        "dump_caluma_config",
        "test-slug",
        model="caluma_form.Form",
        output=temp_file.name,
    )
    assert not json.loads(temp_file.read())

    form, document, questions_dict, answers_dict = form_and_document(
        use_table=True, use_subform=True
    )

    call_command("dumpdata", *FORM_MODELS, output=temp_file.name)

    temp_file.seek(0)
    dumpdata = sort_dump(temp_file.read())

    # remove non-default answers
    dumpdata = [
        d
        for d in dumpdata
        if d["model"] != "caluma_form.answer" or not d["fields"]["document"]
    ]

    form_factory(slug="unrelated")

    call_command(
        "dump_caluma_config", form.pk, model="caluma_form.Form", output=temp_file.name
    )

    temp_file.seek(0)
    dumpcaluma = sort_dump(temp_file.read())

    assert dumpdata == dumpcaluma
    assert not any(
        (obj["model"], obj["pk"]) == ("caluma_form.form", "unrelated")
        for obj in dumpcaluma
    )


@pytest.mark.parametrize(
    "args,kwargs",
    [
        ([], {"model": "caluma_form.Form"}),
        (["foo"], {"format": "jpeg", "model": "caluma_form.Form"}),
        (["foo"], {}),
    ],
)
def test_dump_caluma_config_error(args, kwargs):
    with pytest.raises(CommandError):
        call_command("dump_caluma_config", *args, **kwargs)
