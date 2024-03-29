# Generated by Django 2.2.12 on 2020-06-19 14:21

from django.db import migrations, models

INITIAL_UPDATE = """
    UPDATE caluma_form_historicalanswer histans
    SET history_question_type = hq_latest.type

    FROM (
        SELECT ha.history_id, hq.type, hq.slug, ha.history_date ha_date, hq.history_date hq_date
        FROM caluma_form_historicalanswer ha
        JOIN caluma_form_historicalquestion hq ON hq.slug = ha.question_id AND hq.history_date = (
            SELECT MAX(hq.history_date) FROM caluma_form_historicalquestion hq WHERE (
                hq.slug = ha.question_id AND hq.history_date <= ha.history_date
            )
        )
    ) hq_latest
    WHERE histans.history_id = hq_latest.history_id;
"""

FALLBACK_UPDATE = """
    UPDATE caluma_form_historicalanswer ha
    SET history_question_type = q.type
    FROM caluma_form_question q
    WHERE ha.history_question_type IS NULL AND q.slug = ha.question_id;
"""


class Migration(migrations.Migration):
    dependencies = [("caluma_form", "0034_fix_fk_lengths")]

    operations = [
        migrations.AddField(
            model_name="historicalanswer",
            name="history_question_type",
            field=models.CharField(default=None, max_length=23, null=True),
            preserve_default=False,
        ),
        migrations.RunSQL(INITIAL_UPDATE, reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(FALLBACK_UPDATE, reverse_sql=migrations.RunSQL.noop),
        migrations.AlterField(
            model_name="historicalanswer",
            name="history_question_type",
            field=models.CharField(default="", max_length=23),
            preserve_default=False,
        ),
    ]
