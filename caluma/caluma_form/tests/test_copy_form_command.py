import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from caluma.caluma_form.models import Form


@pytest.mark.parametrize(
    "form__slug,form__name,form__description,form__is_published",
    [("form-v1", "Form v1", "First version of the form", True)],
)
@pytest.mark.parametrize(
    "params,expected_form",
    [
        (
            {"slug": "form-v2"},
            {
                "slug": "form-v2",
                "name": "",
                "description": "",
                "is_published": False,
            },
        ),
        (
            {
                "slug": "form-v2",
                "name": "Form v2",
                "description": "Second version of the form",
                "is_published": True,
            },
            {
                "slug": "form-v2",
                "name": "Form v2",
                "description": "Second version of the form",
                "is_published": True,
            },
        ),
    ],
)
def test_copy_form_command(db, form, params, expected_form):
    call_command("copy_form", form.pk, **params)

    new_form = Form.objects.get(pk=params["slug"])

    for key, value in expected_form.items():
        assert getattr(new_form, key) == value


def test_copy_form_command_error(db):
    with pytest.raises(CommandError) as exc:
        call_command("copy_form", "nonexistent", slug="new-slug")

    assert str(exc.value) == "Form 'nonexistent' not found - can't copy"
