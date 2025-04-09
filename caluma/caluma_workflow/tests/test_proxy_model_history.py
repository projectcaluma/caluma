from caluma.caluma_workflow.models import WorkItem


def test_proxy_model_history(db, work_item):
    class ProxyWorkItem(WorkItem):
        class Meta:
            proxy = True

    proxy_work_item = ProxyWorkItem.objects.get(pk=work_item.pk)

    assert work_item.history.count() == 1
    assert proxy_work_item.history.count() == 1

    proxy_work_item.name = "Foo"
    proxy_work_item.save()

    assert work_item.history.count() == 2
    assert proxy_work_item.history.count() == 2
