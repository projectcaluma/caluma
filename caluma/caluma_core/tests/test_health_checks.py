from django.core import management
from django.urls import reverse
from watchman import settings as watchman_settings


def test_db_connection_working(
    disable_logs, track_errors, capsys, client, snapshot, minio_mock_working, db
):
    """Test /healthz/ endpoint response with working database connection.

    Provide database access through the 'db' fixture with working connection.
    Passes health checks for databases (connection), database models and
    database migrations.
    """
    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert database checks pass
    json_response = response.json()
    assert json_response["databases"] == [{"default": {"ok": True}}]
    assert json_response["database models"] == [{"default": {"ok": True}}]
    assert json_response["database migrations"] == [{"default": {"ok": True}}]
    assert response.status_code == 200

    # assert exception type
    *_, err = capsys.readouterr()
    assert not err


def test_db_connection_broken(
    disable_logs,
    track_errors,
    capsys,
    client,
    snapshot,
    db_broken_connection,
    minio_mock_working,
):
    """Test /healthz/ endpoint response with broken database connection.

    Uses DB fixture with broken connection.
    Affects the health checks for databases (connection), database models and
    database migrations, which should trigger an connection error.
    """
    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert database checks fail
    json_response = response.json()
    assert json_response["databases"] == [{"default": {"ok": False}}]
    assert json_response["database models"] == [{"default": {"ok": False}}]
    assert json_response["database migrations"] == [{"default": {"ok": False}}]
    assert response.status_code == watchman_settings.WATCHMAN_ERROR_CODE

    # assert exception type
    *_, err = capsys.readouterr()
    assert (
        'django.db.utils.OperationalError: could not translate host name "not-db" to address'
        in err
    )


def test_db_model_accessible(
    disable_logs,
    track_errors,
    capsys,
    client,
    snapshot,
    minio_mock_working,
    db_privileges_working,
):
    """Test /healthz/ endpoint response when necessary DB tables are accessible.

    Provide a database connected through a new test user with the necessary
    privileges to access the tables needed in the health checks.
    Passes database models health check and should be able to access the
    necessary model table.
    """
    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert database models check passes
    assert response.json()["database models"] == [{"default": {"ok": True}}]
    assert response.status_code == 200

    # assert exception type
    *_, err = capsys.readouterr()
    assert not err


def test_db_model_read_error(
    disable_logs,
    track_errors,
    capsys,
    client,
    snapshot,
    minio_mock_working,
    db_read_error,
):
    """Test /healthz/ endpoint response when necessary DB tables are inaccessible.

    Provide a database connected through a new test user without the necessary
    privileges to access the tables needed in the health checks.
    Affects the database models health check when trying to access the
    specified model table and triggers a read error due to lack of privileges.
    """
    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert database models check fails
    assert response.json()["database models"] == [{"default": {"ok": False}}]
    assert response.status_code == watchman_settings.WATCHMAN_ERROR_CODE

    # assert exception type
    *_, err = capsys.readouterr()
    assert (
        "django.db.utils.ProgrammingError: permission denied for relation caluma_logging_accesslog"
        in err
    )


def test_db_model_write_error(
    disable_logs,
    track_errors,
    capsys,
    client,
    snapshot,
    minio_mock_working,
    db_write_error,
):
    """Test /healthz/ endpoint response when necessary DB tables are read-only.

    Provide a database connected through a new test user without the necessary
    privileges to write to the tables needed in the health checks.
    Affects the database models health check when trying to create, update or
    delete an object for the specified model table and triggers write error
    due to lack of privileges.
    """
    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert database models check fails
    assert response.json()["database models"] == [{"default": {"ok": False}}]
    assert response.status_code == watchman_settings.WATCHMAN_ERROR_CODE

    # assert exception type
    *_, err = capsys.readouterr()
    assert (
        "django.db.utils.ProgrammingError: permission denied for relation caluma_logging_accesslog"
        in err
    )


def test_minio_connection_working(
    disable_logs, track_errors, capsys, client, snapshot, db, minio_mock_working
):
    """Test /healthz/ endpoint response when minio connection is working.

    Provide minio mock that passes the media storage service health check.
    """
    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert media storage service check passes
    assert response.json()["media storage service"] == {"ok": True}
    assert response.status_code == 200

    # assert exception type
    *_, err = capsys.readouterr()
    assert not err


def test_minio_connection_broken(
    disable_logs, track_errors, capsys, client, snapshot, db, minio_broken_connection
):
    """Test /healthz/ endpoint response when minio connection is broken.

    Provide new minio client with faulty connection information.
    Affects media storage service health check and should trigger
    connection error.
    """
    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert media storage service check fails
    assert response.json()["media storage service"] == {"ok": False}
    assert response.status_code == watchman_settings.WATCHMAN_ERROR_CODE

    # assert exception type
    *_, err = capsys.readouterr()
    assert "urllib3.exceptions.MaxRetryError" in err


def test_minio_not_configured(
    disable_logs, track_errors, capsys, client, snapshot, db, minio_not_configured
):
    """Test /healthz/ endpoint response when minio is not configured.

    Change storage client settings to ensure check assumes no media storage
    service is configured.
    Media storage service health check should pass with a 'not configured'
    annotation.
    """
    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert media storage service check passes
    assert response.json()["media storage service (not configured)"] == {"ok": True}
    assert response.status_code == 200

    # assert exception type
    *_, err = capsys.readouterr()
    assert not err


def test_minio_read_error(
    disable_logs, track_errors, capsys, client, snapshot, db, minio_mock_read_error
):
    """Test /healthz/ endpoint response when minio receives a read error.

    Mocks minio read functions to produce an error.
    Affects media storage service health check file download and stat_object
    functions.
    """
    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert media storage service check fails
    assert response.json()["media storage service"] == {"ok": False}
    assert response.status_code == watchman_settings.WATCHMAN_ERROR_CODE

    # assert exception type
    *_, err = capsys.readouterr()
    assert "Exception: stat_object failed" in err


def test_minio_write_error(
    disable_logs, track_errors, capsys, client, snapshot, db, minio_mock_write_error
):
    """Test /healthz/ endpoint response when minio receives a write error.

    Mocks minio write functions to produce an error.
    Affects media storage service health check file upload function.
    """
    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert media storage service check fails
    assert response.json()["media storage service"] == {"ok": False}
    assert response.status_code == watchman_settings.WATCHMAN_ERROR_CODE

    # assert exception type
    *_, err = capsys.readouterr()
    assert "requests.exceptions.RequestException: PUT request failed" in err


def test_db_migrations_applied(
    disable_logs, track_errors, capsys, client, snapshot, db, minio_mock_working
):
    """Test /healthz/ endpoint response when migrations all created & applied.

    Ensure no changes or unapplied migrations are detected.
    Database migrations health check should pass.
    """
    # Manually migrate database to ensure the database is in the newest
    # state and no unapplied migrations are still around.
    # When running migration tests, database might be left in an
    # inconsistent state.
    management.call_command("migrate")

    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert database migrations check passes
    assert response.json()["database migrations"] == [{"default": {"ok": True}}]
    assert response.status_code == 200

    # assert exception type
    *_, err = capsys.readouterr()
    assert not err


def test_db_migrations_not_applied(
    disable_logs,
    track_errors,
    capsys,
    client,
    snapshot,
    db,
    minio_mock_working,
    roll_back_migrations,
):
    """Test /healthz/ endpoint response when migrations haven't been applied.

    Undo applied migrations for app 'contenttypes'.
    Affects database migrations health check, which should detect unapplied
    migrations and fail.
    """
    # get /healthz/ response and compare to previous snapshot
    response = client.get(reverse("healthz"))
    snapshot.assert_match(response.json())

    # assert database migrations check fails
    assert response.json()["database migrations"] == [{"default": {"ok": False}}]
    assert response.status_code == watchman_settings.WATCHMAN_ERROR_CODE

    # assert exception type
    *_, err = capsys.readouterr()
    assert "Exception: Database has unapplied migrations (migrate)." in err


def test_healthz_disabled(capsys, client, settings):
    """Assert that /healthz endpoint cannot be retrieved if disabled."""
    # disable healthz endpoint
    settings.ENABLE_HEALTHZ_ENDPOINT = False

    # assert accessing health endpoint results in not found error
    response = client.get(reverse("healthz"))
    assert response.status_code == 404

    # assert exception type
    *_, err = capsys.readouterr()
    assert not err
