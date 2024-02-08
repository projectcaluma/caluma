import logging
import sys

import pytest
from django.conf import settings
from django.core import management
from django.db import connection
from psycopg import OperationalError
from watchman.decorators import check as watchman_check_decorator

from caluma.caluma_form import storage_clients


@pytest.fixture
def disable_logs():
    """Disable logs for health checks."""
    urllib3_logger = logging.getLogger("urllib3")
    watchman_logger = logging.getLogger("watchman")

    urllib3_level = urllib3_logger.level
    watchman_disabled = watchman_logger.disabled
    urllib3_logger.setLevel(logging.ERROR)
    watchman_logger.disabled = True

    yield

    urllib3_logger.setLevel(urllib3_level)
    watchman_logger.disabled = watchman_disabled


@pytest.fixture
def track_errors(mocker):
    """Write stacktrace to stderr to enable error checking in tests.

    Patches django-watchman check decorator.
    """

    def track_error_check_decorator(func):
        def wrapped(*args, **kwargs):
            response = watchman_check_decorator(func)(*args, **kwargs)

            if response.get("ok") is False:
                sys.stderr.write(response["stacktrace"])
            elif not response.get("ok"):
                for value in response.values():
                    if value.get("ok") is False:
                        sys.stderr.write(value["stacktrace"])

            return response

        return wrapped

    mocker.patch("watchman.decorators.check", new=track_error_check_decorator)

    yield


@pytest.fixture
def db_broken_connection(transactional_db):
    """DB fixture with broken connection.

    Cap DB connection by trying to re-connect with faulty connection details.
    Changes host settings and restores them after use.
    """
    # overwrite DB host setting and re-connect
    try:
        connection.close()
        prev_settings = settings.DATABASES["default"]["HOST"]
        settings.DATABASES["default"]["HOST"] = "not-db"
        connection.connect()
    except OperationalError:
        # ignore connection error
        pass

    yield

    # restore original DB settings
    connection.close()
    settings.DATABASES["default"]["HOST"] = prev_settings
    connection.connect()


@pytest.fixture
def minio_mock_working(mocker):
    """Provide working minio mock for health checks."""
    return mocker.patch.object(
        storage_clients.client.client, "bucket_exists", return_value=True
    )


@pytest.fixture
def minio_not_configured():
    """Fixture with no connection to minio instance.

    Remove minio client to ensure no connection is available.
    """
    # store previous client
    prev_client = storage_clients.client

    # reset client
    storage_clients.client = None

    yield

    # restore previous client
    storage_clients.client = prev_client


@pytest.fixture
def roll_back_migrations():
    """Roll back database migrations to ensure unapplied migrations exist."""
    # undo applied migrations for app contenttypes
    management.call_command("migrate", "contenttypes", "zero")
    try:
        yield
    finally:
        # re-apply migrations for app contenttypes
        management.call_command("migrate", "contenttypes")
