from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone


def test_add_case_families(transactional_db):
    executor = MigrationExecutor(connection)
    app = "caluma_workflow"
    migrate_from = [(app, "0019_slugfield_length")]
    migrate_to = [(app, "0020_case_families")]

    executor.migrate(migrate_from)
    old_apps = executor.loader.project_state(migrate_from).apps

    # Create some old data. Can't use factories here

    Case = old_apps.get_model(app, "Case")
    Workflow = old_apps.get_model(app, "Workflow")
    WorkItem = old_apps.get_model(app, "WorkItem")
    Task = old_apps.get_model(app, "Task")
    HistoricalCase = old_apps.get_model(app, "HistoricalCase")

    workflow = Workflow.objects.create(slug="main-workflow")

    case = Case.objects.create(workflow=workflow)
    child_case = Case.objects.create(workflow=workflow)
    task = Task.objects.create()
    WorkItem.objects.create(child_case=child_case, case=case, task=task)
    WorkItem.objects.create(child_case=None, case=child_case, task=task)

    historical_case = HistoricalCase.objects.create(
        workflow=workflow,
        id=case.pk,
        created_at=timezone.now(),
        modified_at=timezone.now(),
        history_date=timezone.now(),
    )
    historical__child_case = HistoricalCase.objects.create(
        workflow=workflow,
        id=child_case.pk,
        created_at=timezone.now(),
        modified_at=timezone.now(),
        history_date=timezone.now(),
    )
    historical_orphan_case = HistoricalCase.objects.create(
        workflow=workflow,
        created_at=timezone.now(),
        modified_at=timezone.now(),
        history_date=timezone.now(),
    )

    # Migrate forwards.
    executor.loader.build_graph()  # reload.
    executor.migrate(migrate_to)
    new_apps = executor.loader.project_state(migrate_to).apps

    # Test the new data.
    Case = new_apps.get_model(app, "Case")
    HistoricalCase = new_apps.get_model(app, "HistoricalCase")

    # Refresh objects
    case = Case.objects.get(pk=case.pk)
    historical_case = HistoricalCase.objects.get(pk=historical_case.pk)
    historical__child_case = HistoricalCase.objects.get(pk=historical__child_case.pk)
    historical_orphan_case = HistoricalCase.objects.get(pk=historical_orphan_case.pk)

    for c in Case.objects.iterator():
        assert c.family.pk == case.pk

    assert historical_case.family_id == historical__child_case.family_id == case.id
    assert historical_orphan_case.family_id == historical_orphan_case.id
