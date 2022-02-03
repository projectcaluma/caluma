from django.db import migrations


def get_validators(question):
    return list(
        set([*question.meta.get("formatValidators", []), *question.format_validators])
    )


def forward(apps, schema_editor):
    Question = apps.get_model("caluma_form", "Question")

    for question in Question.objects.filter(meta__formatValidators__isnull=False):
        question.format_validators = get_validators(question)
        del question.meta["formatValidators"]
        question.save()


def reverse(apps, schema_editor):
    Question = apps.get_model("caluma_form", "Question")

    for question in Question.objects.exclude(format_validators=[]):
        question.meta.update({"formatValidators": get_validators(question)})
        question.format_validators = []
        question.save()


class Migration(migrations.Migration):
    dependencies = [
        ("caluma_form", "0043_alter_historicalanswer_history_question_type")
    ]

    operations = [migrations.RunPython(forward, reverse)]
