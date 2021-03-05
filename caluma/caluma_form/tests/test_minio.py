import minio.error
import pytest
import urllib3

from .. import storage_clients


@pytest.mark.parametrize(
    "disable_cert_checks, debug",
    [(False, False), (False, True), (True, False), (True, True)],
)
def test_minio_disable_cert_checks(db, settings, disable_cert_checks, debug):
    settings.MINIO_DISABLE_CERT_CHECKS = disable_cert_checks
    settings.DEBUG = debug

    client = storage_clients.Minio()

    # Some hackery to avoid the test taking too long
    client.client._http.connection_pool_kw["retries"].total = 0

    if debug and disable_cert_checks:
        assert client.client._http.connection_pool_kw["cert_reqs"] == "CERT_NONE"

        # This should succeed, as we're not verifying the server certificate
        client.client._http.urlopen("get", "https://self-signed.badssl.com/")
    else:
        assert client.client._http.connection_pool_kw["cert_reqs"] == "CERT_REQUIRED"

        with pytest.raises(urllib3.exceptions.RequestError):
            # This should fail, as we are in fact verifying certificates
            client.client._http.urlopen("get", "https://self-signed.badssl.com/")


def _put_side_effect(*_, **__):
    # first call, raise an exception, second time, succeed
    yield minio.error.S3Error(
        "NoSuchBucket",
        "Bucket does not exist",
        resource="adsf",
        request_id="fake",
        host_id="fake",
        response="fake",
    )
    yield "upload_url_successful"


@pytest.fixture
def patched_minio(mocker):
    make_bucket = mocker.patch("minio.api.Minio.make_bucket")
    put_object = mocker.patch(
        "minio.api.Minio.presigned_put_object", side_effect=_put_side_effect()
    )
    return make_bucket, put_object


def test_minio_auto_create_bucket_enabled(db, settings, patched_minio):
    settings.MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
    client = storage_clients.Minio()

    make_bucket, _ = patched_minio

    assert client.upload_url("asdf") == "upload_url_successful"
    assert make_bucket.call_count == 1


def test_minio_auto_create_bucket_disabled(db, settings, patched_minio):
    settings.MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = False
    client = storage_clients.Minio()
    make_bucket, _ = patched_minio

    with pytest.raises(minio.error.S3Error):
        client.upload_url("asdf")

    assert make_bucket.call_count == 0


@pytest.mark.parametrize("exc_code", ["NoSuchBucket", "NoSuchKey"])
def test_minio_handle_exceptions(exc_code, caplog, mocker):
    # The "happy path" is tested in various places already
    mocker.patch(
        "minio.api.Minio.stat_object",
        side_effect=minio.error.S3Error(
            code=exc_code,
            message="",
            resource="test_object",
            request_id="",
            host_id="",
            response=None,
        ),
    )
    client = storage_clients.Minio()
    stat = client.stat_object("test_object")
    assert stat is None
    assert caplog.messages == [f"Minio error, cannot stat object: {exc_code}"]
