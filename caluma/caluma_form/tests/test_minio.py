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
