# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-19 17:20
from __future__ import unicode_literals

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("caluma_form", "0007_auto_20190208_1232")]

    operations = [
        migrations.AlterField(
            model_name="answer",
            name="value",
            field=models.JSONField(
                blank=True,
                encoder=django.core.serializers.json.DjangoJSONEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="type",
            field=models.CharField(
                choices=[
                    ("multiple_choice", "multiple_choice"),
                    ("integer", "integer"),
                    ("float", "float"),
                    ("date", "date"),
                    ("choice", "choice"),
                    ("textarea", "textarea"),
                    ("text", "text"),
                    ("table", "table"),
                ],
                max_length=15,
            ),
        ),
    ]
