import importlib

import pytest
from django.apps.registry import apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone

from caluma.caluma_workflow.models import Case


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


@pytest.mark.parametrize(
    "set_parent_work_item, set_family_none",
    [(False, False), (False, True), (True, False), (True, True)],
)
def test_set_family_with_broken_data(
    db, case_factory, work_item_factory, set_parent_work_item, set_family_none
):
    parent, child, unrelated = case_factory.create_batch(3)

    Case.objects.all().update(family=None)  # not sure why factory doesn't allow this

    child.parent_work_item = (
        work_item_factory(case=parent) if set_parent_work_item else None
    )
    child.save()
    if set_parent_work_item:
        child.parent_work_item.case = unrelated if set_family_none else parent
        child.parent_work_item.save()

    migra_module = importlib.import_module(
        "caluma.caluma_workflow.migrations.0020_case_families"
    )

    class FakeEditor:
        connection = connection

    migra_module.set_family(apps, schema_editor=FakeEditor)


def test_workitem_name_description(transactional_db):
    executor = MigrationExecutor(connection)
    app = "caluma_workflow"
    migrate_from = [(app, "0021_work_item_controlling_groups")]
    migrate_to = [(app, "0022_workitem_name_description")]

    executor.migrate(migrate_from)
    old_apps = executor.loader.project_state(migrate_from).apps

    # Create some old data. Can't use factories here

    Case = old_apps.get_model(app, "Case")
    Workflow = old_apps.get_model(app, "Workflow")
    WorkItem = old_apps.get_model(app, "WorkItem")
    Task = old_apps.get_model(app, "Task")
    HistoricalWorkItem = old_apps.get_model(app, "HistoricalWorkItem")

    workflow = Workflow.objects.create(slug="main-workflow")

    case = Case.objects.create(workflow=workflow)
    task = Task.objects.create(name="task_name", description="task_description")
    work_item = WorkItem.objects.create(child_case=None, case=case, task=task)

    HistoricalWorkItem.objects.create(
        id=work_item.pk,
        child_case=None,
        case=case,
        task=task,
        created_at=timezone.now(),
        modified_at=timezone.now(),
        history_date=timezone.now(),
    )

    HistoricalWorkItem.objects.create(
        id=work_item.pk,
        child_case=None,
        case=case,
        task=task,
        created_at=timezone.now() + timezone.timedelta(hours=1),
        modified_at=timezone.now() + timezone.timedelta(hours=1),
        history_date=timezone.now() + timezone.timedelta(hours=1),
    )

    # Migrate forwards.
    executor.loader.build_graph()  # reload.
    executor.migrate(migrate_to)
    new_apps = executor.loader.project_state(migrate_to).apps

    # Test the new data.
    WorkItem = new_apps.get_model(app, "WorkItem")
    HistoricalWorkItem = new_apps.get_model(app, "HistoricalWorkItem")

    # Refresh objects
    work_item = WorkItem.objects.get(pk=work_item.pk)
    historical_work_items = HistoricalWorkItem.objects.filter(id=work_item.pk)

    for wi in [work_item, *historical_work_items]:
        assert wi.name == wi.task.name
        assert wi.description == wi.task.description
