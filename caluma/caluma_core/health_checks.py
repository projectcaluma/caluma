import uuid
from io import StringIO

import requests
from django.conf import settings
from django.core import management
from watchman.decorators import check

from caluma.caluma_form import storage_clients
from caluma.caluma_logging.models import AccessLog


@check
def _check_pending_migrations(db_name):
    """Check database for pending migrations.

    Returns JSON mapping if no pending migrations, otherwise raises Exception.
    @check django-watchman decorator catches and handles exceptions.
    """
    # check for unapplied migrations
    out = StringIO()
    management.call_command("showmigrations", "--plan", stdout=out)
    plan = out.getvalue()
    if "[ ]" in plan:
        raise Exception("Database has unapplied migrations (migrate).")

    return {db_name: {"ok": True}}


@check
def _check_media_storage_service():
    """Check media storage service connection and operations."""
    # generate object name
    storage_client = storage_clients.client
    prefix = "healthz_tmp-object_"
    object_name = prefix + str(uuid.uuid4())

    try:
        # request upload url and upload
        upload_url = storage_client.upload_url(object_name)

        filename = "healthz_tmp-file.txt"
        content = "Test\nTest\n"
        files = {"file": (filename, content)}
        upload_request = requests.put(upload_url, files=files)
        assert upload_request.status_code == 200

        # stat object
        stat = storage_client.stat_object(object_name)
        assert stat.object_name == object_name

        # request download url and download file
        download_url = storage_client.download_url(object_name)

        download_request = requests.get(download_url)
        assert download_request.status_code == 200
        assert filename in download_request.text and content in download_request.text

        # remove object
        storage_client.remove_object(object_name)
        assert not storage_client.stat_object(object_name)

        return {"ok": True}

    finally:
        storage_client.remove_object(object_name)


@check
def _check_models(database):
    """Check model instantion and operations on database."""
    log = None
    try:
        # Instantiate model
        log = AccessLog.objects.create(status_code=22)
        assert (
            log in AccessLog.objects.all()
        ), "Failed to save model instance to database."

        # Retrieve object
        retrieved_log = AccessLog.objects.get(pk=log.pk)
        assert log == retrieved_log, "Unexpected object retrieved from database."
        assert (
            retrieved_log.status_code == log.status_code
        ), "Unexpected object data retrieved from database."

        # Update object
        log.status_code = 42
        log.save()
        retrieved_log = AccessLog.objects.get(pk=log.pk)
        assert log == retrieved_log, "Unexpected object retrieved from database."
        assert (
            retrieved_log.status_code == log.status_code
        ), "Unexpected object data retrieved from database."

        # Remove object
        log.delete()
        log = None
        assert (
            log not in AccessLog.objects.all()
        ), "Failed to delete model instance from database."

        return {database: {"ok": True}}

    finally:
        # Cleanup
        if log:  # pragma: no cover
            log.delete()


def check_media_storage_service():
    """Check media storage service connection and operations."""
    # Check if media storage service is available
    if not storage_clients.client:
        return {"media storage service (not configured)": {"ok": True}}

    return {"media storage service": _check_media_storage_service()}


def check_migrations():
    """Check available databases for unapplied migrations."""
    databases = sorted(settings.DATABASES)
    checked_databases = [_check_pending_migrations(db_name) for db_name in databases]

    return {"database migrations": checked_databases}


def check_models():
    """Check model instantiation."""
    databases = sorted(settings.DATABASES)
    checked_databases = [_check_models(db_name) for db_name in databases]

    return {"database models": checked_databases}
