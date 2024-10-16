# Generated by Django 4.2.16 on 2024-10-16 09:40

import uuid_extensions.uuid7
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("caluma_analytics", "0007_add_analytics_description_field"),
    ]

    operations = [
        migrations.AlterField(
            model_name="analyticsfield",
            name="id",
            field=models.UUIDField(
                default=uuid_extensions.uuid7,
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="historicalanalyticsfield",
            name="id",
            field=models.UUIDField(
                db_index=True, default=uuid_extensions.uuid7, editable=False
            ),
        ),
    ]
