from django.db import migrations

from caluma.caluma_form.models import Question


def remove_value(apps, schema_editor):
    apps.get_model("caluma_form", "Answer").objects.filter(
        question__type=Question.TYPE_TABLE, value__isnull=False
    ).update(value=None)


class Migration(migrations.Migration):
    dependencies = [("caluma_form", "0037_default_answer_one2one")]
    operations = [migrations.RunPython(remove_value, migrations.RunPython.noop)]
