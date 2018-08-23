# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-23 15:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("form", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="form",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="form",
            name="is_published",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="question",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
    ]
