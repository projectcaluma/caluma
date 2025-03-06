from django.db.models import Manager, QuerySet

from caluma.caluma_core.managers import register_custom_managers
from caluma.caluma_workflow.models import WorkItem


class MyCustomQuerySet(QuerySet):
    def only_ready(self):
        return self.filter(status=WorkItem.STATUS_READY)

    class Meta:
        model = WorkItem
        name = "my_queryset"


class MyCustomManager(Manager):
    def only_canceled(self):
        return self.filter(status=WorkItem.STATUS_CANCELED)

    class Meta:
        model = WorkItem
        name = "my_manager"


def test_custom_managers(db, settings, work_item_factory):
    settings.MANAGER_CLASSES = [
        "caluma.caluma_core.tests.test_managers.MyCustomQuerySet",
        "caluma.caluma_core.tests.test_managers.MyCustomManager",
    ]
    register_custom_managers()

    ready_work_item = work_item_factory(status=WorkItem.STATUS_READY)
    canceled_work_item = work_item_factory(status=WorkItem.STATUS_CANCELED)

    assert hasattr(WorkItem, "my_queryset")
    ready_work_items = WorkItem.my_queryset.only_ready()
    assert ready_work_items.count() == 1
    assert ready_work_items.first() == ready_work_item

    assert hasattr(WorkItem, "my_manager")
    canceled_work_item_work_items = WorkItem.my_manager.only_canceled()
    assert canceled_work_item_work_items.count() == 1
    assert canceled_work_item_work_items.first() == canceled_work_item
