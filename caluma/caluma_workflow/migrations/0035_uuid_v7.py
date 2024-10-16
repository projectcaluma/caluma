# Generated by Django 4.2.16 on 2024-10-16 09:40

import uuid_extensions.uuid7
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("caluma_workflow", "0034_workitem_caluma_work_created_c87fd3_idx_and_more")
    ]

    operations = [
        migrations.AlterField(
            model_name="case",
            name="id",
            field=models.UUIDField(
                default=uuid_extensions.uuid7,
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="flow",
            name="id",
            field=models.UUIDField(
                default=uuid_extensions.uuid7,
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="historicalcase",
            name="id",
            field=models.UUIDField(
                db_index=True, default=uuid_extensions.uuid7, editable=False
            ),
        ),
        migrations.AlterField(
            model_name="historicalflow",
            name="id",
            field=models.UUIDField(
                db_index=True, default=uuid_extensions.uuid7, editable=False
            ),
        ),
        migrations.AlterField(
            model_name="historicaltaskflow",
            name="id",
            field=models.UUIDField(
                db_index=True, default=uuid_extensions.uuid7, editable=False
            ),
        ),
        migrations.AlterField(
            model_name="historicalworkitem",
            name="id",
            field=models.UUIDField(
                db_index=True, default=uuid_extensions.uuid7, editable=False
            ),
        ),
        migrations.AlterField(
            model_name="taskflow",
            name="id",
            field=models.UUIDField(
                default=uuid_extensions.uuid7,
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="workitem",
            name="id",
            field=models.UUIDField(
                default=uuid_extensions.uuid7,
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
