import os

import pytest
from django.conf import settings
from django.core.management import call_command
from minio import Minio
from simple_history.models import registered_models

from caluma.caluma_form.models import Document, Form

from ..management.commands import cleanup_history


def test_create_bucket_command(mocker):
    mocker.patch.object(Minio, "make_bucket")
    call_command("create_bucket", stdout=open(os.devnull, "w"))
    Minio.make_bucket.assert_called_once_with(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME)


@pytest.mark.parametrize("force", [True, False])
@pytest.mark.parametrize("dangling", [True, False])
def test_cleanup_history_command(db, force, dangling):
    # we need to override the registered models dict in order to get rid of the
    # fake models created in caluma_core tests
    cleanup_history.registered_models = {
        k: v for k, v in registered_models.items() if not k.startswith("caluma_core_")
    }
    kwargs = {}
    if force:
        kwargs["force"] = force
    if dangling:
        kwargs["dangling"] = dangling

    f1 = Form.objects.create(slug="form 1")

    doc = Document.objects.create(form=f1)
    assert Document.history.count() == 1

    doc.delete()
    f1.delete()

    # created 4 history entries:
    # HistoricalForm: 2 (1 created, 1 deleted)
    # HistoricalDocument: 2 (1 created, 1 deleted)

    call_command("cleanup_history", **kwargs, stdout=open(os.devnull, "w"))

    assert Form.history.count() == 2
    assert Document.history.count() == 0 if (dangling and force) else 2
