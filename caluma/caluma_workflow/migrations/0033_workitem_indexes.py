# Generated by Django 4.2.16 on 2024-09-26 08:21

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caluma_workflow', '0032_alter_workflow_start_tasks'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='workitem',
            index=models.Index(fields=['status'], name='caluma_work_status_4d2ecc_idx'),
        ),
        migrations.AddIndex(
            model_name='workitem',
            index=django.contrib.postgres.indexes.GinIndex(fields=['controlling_groups'], name='caluma_work_control_6ede39_gin'),
        ),
    ]