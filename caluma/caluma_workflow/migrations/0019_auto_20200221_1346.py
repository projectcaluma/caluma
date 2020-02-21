# Generated by Django 2.2.10 on 2020-02-21 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caluma_workflow', '0018_auto_20200219_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaltask',
            name='slug',
            field=models.SlugField(max_length=120),
        ),
        migrations.AlterField(
            model_name='historicalworkflow',
            name='slug',
            field=models.SlugField(max_length=120),
        ),
        migrations.AlterField(
            model_name='task',
            name='slug',
            field=models.SlugField(max_length=120, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='slug',
            field=models.SlugField(max_length=120, primary_key=True, serialize=False),
        ),
    ]
