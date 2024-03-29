# Generated by Django 2.2.6 on 2019-10-31 12:22

from django.db import migrations

import caluma.caluma_core.models


class Migration(migrations.Migration):
    dependencies = [("caluma_workflow", "0014_add_gin_index_to_jsonfields")]

    operations = [
        migrations.AlterField(
            model_name="historicalworkitem",
            name="status",
            field=caluma.caluma_core.models.ChoicesCharField(
                choices=[
                    ("ready", "Task is ready to be processed."),
                    ("completed", "Task is done."),
                    ("canceled", "Task is cancelled."),
                    ("skipped", "Task is skipped."),
                ],
                db_index=True,
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="workitem",
            name="status",
            field=caluma.caluma_core.models.ChoicesCharField(
                choices=[
                    ("ready", "Task is ready to be processed."),
                    ("completed", "Task is done."),
                    ("canceled", "Task is cancelled."),
                    ("skipped", "Task is skipped."),
                ],
                db_index=True,
                max_length=50,
            ),
        ),
    ]
