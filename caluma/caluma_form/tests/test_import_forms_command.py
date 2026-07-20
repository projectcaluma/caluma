import textwrap

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from caluma.caluma_form.models import (
    Form,
    FormQuestion,
    Option,
    Question,
    QuestionOption,
)


@pytest.mark.parametrize("tmp_file_suffix", [".yaml"])
def test_import_forms_command_defaults(db, tmp_path, tmp_file_suffix):
    content = textwrap.dedent(
        """
        forms:
          - label: Main Form
            questions:
              - label: Free Text
              - label: Pick One
                options:
                  - First Option
                  - label: Second Option
        """
    )
    file_path = tmp_path / f"forms{tmp_file_suffix}"
    file_path.write_text(content)

    call_command("import_forms", str(file_path))

    form = Form.objects.get(pk="main-form")
    assert form.name == "Main Form"

    text_question = Question.objects.get(pk="free-text")
    choice_question = Question.objects.get(pk="pick-one")

    assert text_question.type == Question.TYPE_TEXT
    assert text_question.is_required == "false"
    assert choice_question.type == Question.TYPE_CHOICE

    options = list(
        Option.objects.filter(
            slug__in=["pick-one-first-option", "pick-one-second-option"]
        ).order_by("slug")
    )
    assert [opt.slug for opt in options] == [
        "pick-one-first-option",
        "pick-one-second-option",
    ]

    form_question_slugs = set(
        FormQuestion.objects.filter(form=form).values_list("question_id", flat=True)
    )
    assert form_question_slugs == {"free-text", "pick-one"}

    choice_option_slugs = set(
        QuestionOption.objects.filter(question=choice_question).values_list(
            "option_id", flat=True
        )
    )
    assert choice_option_slugs == {"pick-one-first-option", "pick-one-second-option"}


def test_import_forms_command_table_reference(db, tmp_path):
    file_path = tmp_path / "forms.yaml"
    file_path.write_text(
        textwrap.dedent(
            """
            forms:
              - slug: row-form
                label: Row Form
                questions:
                  - label: Row Question
              - slug: main-form
                label: Main Form
                questions:
                  - label: Rows
                    type: table
                    row_form: row-form
            """
        )
    )

    call_command("import_forms", str(file_path))

    table_question = Question.objects.get(pk="rows")
    assert table_question.type == Question.TYPE_TABLE
    assert table_question.row_form_id == "row-form"


def test_import_forms_command_aborts_on_existing_entity_without_update(
    db, tmp_path, form_factory
):
    form_factory(slug="main-form")

    file_path = tmp_path / "forms.yaml"
    file_path.write_text(
        textwrap.dedent(
            """
            forms:
              - slug: main-form
                label: Main Form
                questions: []
            """
        )
    )

    with pytest.raises(CommandError) as exc:
        call_command("import_forms", str(file_path))

    assert str(exc.value) == "Form 'main-form' already exists"


def test_import_forms_command_updates_with_flag(
    db, tmp_path, form_factory, question_factory
):
    form = form_factory(slug="main-form", name="Old Name")
    first = question_factory(slug="first", type=Question.TYPE_TEXT)
    second = question_factory(slug="second", type=Question.TYPE_TEXT)
    FormQuestion.objects.create(form=form, question=first, sort=2)
    FormQuestion.objects.create(form=form, question=second, sort=1)

    file_path = tmp_path / "forms.yaml"
    file_path.write_text(
        textwrap.dedent(
            """
            forms:
              - slug: main-form
                label: Updated Name
                questions:
                  - slug: second
                    label: Second Updated
                  - slug: first
                    label: First Updated
            """
        )
    )

    call_command("import_forms", str(file_path), "--update")

    form.refresh_from_db()
    assert form.name == "Updated Name"

    first.refresh_from_db()
    second.refresh_from_db()
    assert first.label == "First Updated"
    assert second.label == "Second Updated"

    ordered = list(
        form.questions.all()
        .order_by("formquestion__sort")
        .values_list("slug", flat=True)
    )
    assert ordered == ["first", "second"]


def test_import_forms_command_rolls_back_on_invalid_reference(db, tmp_path):
    file_path = tmp_path / "forms.yaml"
    file_path.write_text(
        textwrap.dedent(
            """
            forms:
              - slug: main-form
                label: Main Form
                questions:
                  - label: Rows
                    type: table
                    row_form: missing-row-form
            """
        )
    )

    with pytest.raises(CommandError) as exc:
        call_command("import_forms", str(file_path))

    assert "unknown" in str(exc.value)
    assert not Form.objects.filter(pk="main-form").exists()
    assert not Question.objects.filter(pk="rows").exists()


def test_import_forms_command_dry_run(db, tmp_path):
    file_path = tmp_path / "forms.yaml"
    file_path.write_text(
        textwrap.dedent(
            """
            forms:
              - label: Main Form
                questions:
                  - label: First
            """
        )
    )

    call_command("import_forms", str(file_path), "--dry-run")

    assert Form.objects.count() == 0
    assert Question.objects.count() == 0


def test_import_forms_command_file_language(db, tmp_path):
    file_path = tmp_path / "forms.yaml"
    file_path.write_text(
        textwrap.dedent(
            """
            language: de
            forms:
              - label: Hauptformular
                questions:
                  - label: Freitext
            """
        )
    )

    call_command("import_forms", str(file_path))

    form = Form.objects.get(pk="hauptformular")
    question = Question.objects.get(pk="freitext")
    assert form.name["de"] == "Hauptformular"
    assert question.label["de"] == "Freitext"
