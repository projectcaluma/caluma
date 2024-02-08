from io import StringIO

from django.conf import settings
from django.core import management
from watchman.decorators import check

from caluma.caluma_form import storage_clients


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
    """Check media storage service connectivity."""
    return {
        "ok": storage_clients.client.client.bucket_exists(
            settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
        )
    }


def check_media_storage_service():
    """Check media storage service connectivity."""
    # Check if media storage service is available
    if not storage_clients.client:
        return {"media storage service (not configured)": {"ok": True}}

    return {"media storage service": _check_media_storage_service()}


def check_migrations():
    """Check available databases for unapplied migrations."""
    databases = sorted(settings.DATABASES)
    checked_databases = [_check_pending_migrations(db_name) for db_name in databases]

    return {"database migrations": checked_databases}
