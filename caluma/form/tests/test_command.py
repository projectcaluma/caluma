import os

from django.conf import settings
from django.core.management import call_command
from minio import Minio


def test_create_bucket_command(mocker):
    mocker.patch.object(Minio, "make_bucket")
    call_command("create_bucket", stdout=open(os.devnull, "w"))
    Minio.make_bucket.assert_called_once_with(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME)
