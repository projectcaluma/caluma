import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from caluma.caluma_analytics import simple_table


def test_migrate_rename_form_slugs(post_migrate_to_current_state):
    executor = MigrationExecutor(connection)
    migrate_from = [
        ("caluma_analytics", "0005_analytics_field_ordering"),
        ("caluma_form", "0046_file_answer_reverse_keys"),
    ]
    migrate_to = [("caluma_analytics", "0006_rename_form_slug_fields")]

    executor.migrate(migrate_from)
    old_apps = executor.loader.project_state(migrate_from).apps

    # Create some old data. Can't use factories here
    Document = old_apps.get_model("caluma_form", "Document")
    Form = old_apps.get_model("caluma_form", "Form")
    Answer = old_apps.get_model("caluma_form", "Answer")
    Question = old_apps.get_model("caluma_form", "Question")
    FormQuestion = old_apps.get_model("caluma_form", "FormQuestion")

    AnalyticsTable = old_apps.get_model("caluma_analytics", "AnalyticsTable")

    main_form = Form.objects.create(slug="main-form")

    main_text_question = Question.objects.create(type="text", slug="main-text-question")
    FormQuestion.objects.create(form=main_form, question=main_text_question)

    main_document = Document.objects.create(form=main_form)
    Answer.objects.create(
        value="dolor sit", question=main_text_question, document=main_document
    )

    # Create an analytics table
    table = AnalyticsTable.objects.create(
        slug="migration-testing", name="Test", starting_object="documents"
    )
    table.fields.create(data_source="form_id", alias="the_form")

    runner = simple_table.SimpleTable(table)

    with pytest.raises(KeyError) as exc_info:
        # simple table is the "new" code, which already cannot handle
        # `form_id` data source anymore.
        runner.get_records()
    assert exc_info.value.args == ("form_id",)
    assert type(exc_info.value) == KeyError

    # Migrate forwards.
    executor.loader.build_graph()  # reload.
    executor.migrate(migrate_to)
    new_apps = executor.loader.project_state(migrate_to).apps

    # Test the new data.
    AnalyticsTable = new_apps.get_model("caluma_analytics", "AnalyticsTable")

    new_table = AnalyticsTable.objects.get(slug="migration-testing")
    new_runner = simple_table.SimpleTable(new_table)

    # Now that the data source is migrated, we should see results
    records = new_runner.get_records()
    assert records == [{"the_form": main_form.slug}]
