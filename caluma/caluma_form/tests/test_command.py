import os

import pytest
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from minio import Minio
from simple_history.models import registered_models

from caluma.caluma_core.management.commands import cleanup_history

from ..models import Document, Form


def test_create_bucket_command(mocker):
    mocker.patch.object(Minio, "make_bucket")
    call_command("create_bucket", stdout=open(os.devnull, "w"))
    Minio.make_bucket.assert_called_once_with(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME)


@pytest.mark.parametrize("force", [True, False])
@pytest.mark.parametrize("keep,kept", [("1 year", 5), ("1 day", 4), (None, 5)])
@pytest.mark.parametrize("dangling", [True, False])
def test_cleanup_history_command(db, force, keep, kept, dangling):
    # we need to override the registered models dict in order to get rid of the
    # fake models created in caluma_core tests
    cleanup_history.registered_models = {
        k: v for k, v in registered_models.items() if not k.startswith("caluma_core_")
    }
    kwargs = {}
    if force:
        kwargs["force"] = force
    else:
        kept = 6
    if keep:
        kwargs["keep"] = keep

    kwargs["dangling"] = dangling

    f1 = Form.objects.create(slug="form 1")

    f2 = Form.objects.create(slug="form 2")
    f2_hist = f2.history.first()
    f2_hist.history_date = f2_hist.history_date - timezone.timedelta(days=2)
    f2_hist.save()

    f3 = Form.objects.create(slug="form 3")
    f3_hist = f3.history.first()
    f3_hist.history_date = f3_hist.history_date - timezone.timedelta(days=730)
    f3_hist.save()

    doc = Document.objects.create(form=f1)
    assert Document.history.count() == 1

    doc.delete()
    f1.delete()

    # created 5 history entries:
    # HistoricalForm: 4 (3 created, 1 deleted)
    # HistoricalDocument: 2 (1 created, 1 deleted)

    call_command("cleanup_history", **kwargs, stdout=open(os.devnull, "w"))

    assert Form.history.count() + Document.history.count() == kept - 2 * int(
        dangling and force
    )
