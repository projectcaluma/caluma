import logging
import sys

import pytest
import requests
from django.conf import settings
from django.core import management
from django.db import connection
from minio import Minio
from psycopg2 import OperationalError
from requests.models import Response
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


def switch_user(test=False):
    """Re-connect to database with either user 'tester' or 'caluma'."""
    # set username and password
    user = "tester" if test else "caluma"
    password = "test" if test else "caluma"

    # connect new user to database
    connection.close()
    settings.DATABASES["default"]["USER"] = user
    settings.DATABASES["default"]["PASSWORD"] = password
    connection.connect()


@pytest.fixture
def db_user_tester(transactional_db):
    """Create new user 'tester' with privileges necessary for health checks.

    User is removed after use.
    """
    # get db connection
    cursor = connection.cursor()

    # create test user (with all necessary privileges)
    cursor.execute("CREATE USER tester WITH PASSWORD 'test';")
    cursor.execute("GRANT ALL ON caluma_logging_accesslog TO tester;")
    cursor.execute("GRANT ALL ON caluma_form_file TO tester;")
    cursor.execute(
        "GRANT USAGE, SELECT ON SEQUENCE caluma_logging_accesslog_id_seq TO tester;"
    )
    cursor.execute("GRANT ALL ON django_migrations TO tester;")

    yield

    # get db connection
    cursor = connection.cursor()

    # revoke privileges and remove user
    cursor.execute("REVOKE ALL ON caluma_logging_accesslog FROM tester;")
    cursor.execute("REVOKE ALL ON caluma_form_file FROM tester;")
    cursor.execute(
        "REVOKE USAGE, SELECT ON SEQUENCE caluma_logging_accesslog_id_seq FROM tester;"
    )
    cursor.execute("REVOKE ALL ON django_migrations FROM tester;")
    cursor.execute("DROP USER tester;")


@pytest.fixture
def db_privileges_working(db_user_tester):
    """DB fixture with all necessary privileges for health checks.

    Create new test user with necessary privileges and connect to database.
    Remove test user and reconnect with original database user after use.
    """
    # switch to new test user
    switch_user(test=True)

    yield

    # switch back to caluma user
    switch_user()


@pytest.fixture
def db_read_error(db_user_tester):
    """DB fixture with revoked read privileges on caluma_logging_accesslog.

    Create new test user without necessary read privileges for table used by
    health check and connect to database.
    Remove test user and reconnect with original database user after use.
    """
    # revoke select rights on accesslog table
    cursor = connection.cursor()
    cursor.execute("REVOKE SELECT ON caluma_logging_accesslog FROM tester;")

    # switch to new test user
    switch_user(test=True)

    yield

    # switch back to caluma user
    switch_user()

    # grant select rights on accesslog table such that user can be removed
    cursor = connection.cursor()
    cursor.execute("GRANT SELECT ON caluma_logging_accesslog TO tester;")


@pytest.fixture
def db_write_error(db_user_tester):
    """DB fixture with revoked write privileges on caluma_logging_accesslog.

    Create new test user without necessary write privileges for table used by
    health check and connect to database.
    Remove test user and reconnect with original database user after use.
    """
    # revoke insert, update and delete privileges on accesslog table
    cursor = connection.cursor()
    cursor.execute(
        "REVOKE INSERT,UPDATE,DELETE ON caluma_logging_accesslog FROM tester;"
    )

    # switch to new test user
    switch_user(test=True)

    yield

    # switch back to caluma user
    switch_user()

    # grant insert, update, delete rights on accesslog table
    # such that user can be removed
    cursor = connection.cursor()
    cursor.execute("GRANT INSERT,UPDATE,DELETE ON caluma_logging_accesslog TO tester;")


@pytest.fixture
def minio_mock_working(minio_mock, mocker):
    """Provide working minio mock for health checks.

    Based on existing minio_mock.
    Patches requests.get and requests.put to provide necessary responses for
    health check.
    """
    # determine fixed UUID to be used during tests
    uuid = "7c5ad424-e351-4db8-ba37-bbace45d0e0f"
    mocker.patch("uuid.uuid4", return_value=uuid)

    # mock upload response
    upload_response = Response()
    upload_response.status_code = 200
    mocker.patch("requests.put", return_value=upload_response)

    # mock download response
    download_response = Response()
    download_response.status_code = 200
    download_response._content = (
        b"--ffc537c8d0da305912d6440576ac0d75\r\n"
        b'Content-Disposition: form-data; name="file"; '
        b'filename="healthz_tmp-file.txt"\r\n\r\n'
        b"Test\nTest\n\r\n"
        b"--ffc537c8d0da305912d6440576ac0d75--\r\n"
    )
    mocker.patch("requests.get", return_value=download_response)

    # change object name of existing stat response
    stat_response = Minio.stat_object.return_value
    stat_response._object_name = "healthz_tmp-object_" + uuid

    # update responses compatible with media storage service health check
    Minio.stat_object.side_effect = [stat_response, None]


@pytest.fixture
def minio_broken_connection():
    """Provide new minio client with faulty connection details.

    Change minio settings to generate new client unable to connect to minio
    instance.
    Restore original settings and client after use.
    """
    # store previous client
    prev_client = storage_clients.client

    # reconnect with new client (with invalid host settings)
    prev_settings = settings.MINIO_STORAGE_ENDPOINT
    settings.MINIO_STORAGE_ENDPOINT = "not-minio:9000"
    storage_clients.client = storage_clients.Minio()

    yield

    # restore previous client
    settings.MINIO_STORAGE_ENDPOINT = prev_settings
    storage_clients.client = prev_client


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
def minio_mock_read_error(minio_mock, mocker):
    """Produce exception when downloading file or stat-ing object.

    This scenario might occur when there is a internal minio issue or if a
    previous upload isn't successful (which doesn't issue exception).
    """
    # raise exception instead of handling request
    def download_side_effect(*args, **kwargs):  # pragma: no cover
        raise requests.exceptions.RequestException("GET request failed")

    def stat_side_effect(*args, **kwargs):
        raise Exception("stat_object failed")

    # determine fixed UUID to be used during tests
    uuid = "7c5ad424-e351-4db8-ba37-bbace45d0e0f"
    mocker.patch("uuid.uuid4", return_value=uuid)

    # mock upload response
    upload_response = Response()
    upload_response.status_code = 200
    mocker.patch("requests.put", return_value=upload_response)

    # mock erroneous download response
    download_response = Response()
    download_response.status_code = 500
    mocker.patch(
        "requests.get", return_value=download_response, side_effect=download_side_effect
    )

    # raise exception
    Minio.stat_object.side_effect = stat_side_effect


@pytest.fixture
def minio_mock_write_error(minio_mock, mocker):
    """Produce exception when uploading file.

    This scenario might occur when there is a internal minio issue.
    """
    # raise exception instead of handling request
    def upload_side_effect(*args, **kwargs):
        raise requests.exceptions.RequestException("PUT request failed")

    # determine fixed UUID to be used during tests
    uuid = "7c5ad424-e351-4db8-ba37-bbace45d0e0f"
    mocker.patch("uuid.uuid4", return_value=uuid)

    # mock upload response
    upload_response = Response()
    upload_response.status_code = 500
    mocker.patch(
        "requests.put", return_value=upload_response, side_effect=upload_side_effect
    )

    # mock download response
    download_response = Response()
    download_response.status_code = 200
    download_response._content = (
        b"--ffc537c8d0da305912d6440576ac0d75\r\n"
        b'Content-Disposition: form-data; name="file"; '
        b'filename="healthz_tmp-file.txt"\r\n\r\n'
        b"Test\nTest\n\r\n"
        b"--ffc537c8d0da305912d6440576ac0d75--\r\n"
    )
    mocker.patch("requests.get", return_value=download_response)

    # change object name of existing stat response
    stat_response = Minio.stat_object.return_value
    stat_response._object_name = "healthz_tmp-object_" + uuid

    # update responses compatible with media storage service health check
    Minio.stat_object.side_effect = [stat_response, None]


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
