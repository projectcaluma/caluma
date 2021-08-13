# Generated by Django 2.2.20 on 2021-08-13 08:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("caluma_form", "0040_add_modified_by_user_group"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dynamicoption",
            name="document",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="dynamic_options",
                to="caluma_form.Document",
            ),
        ),
    ]
