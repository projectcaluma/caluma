from datetime import timedelta
from functools import wraps
from logging import getLogger

import minio
import urllib3
from django.conf import settings
from minio.commonconfig import CopySource
from minio.error import S3Error

log = getLogger(__name__)


class Retry(BaseException):
    pass


def _retry_on_missing_bucket(fn):
    """Create missing bucket if needed (decorator).

    If enabled in the settings, try to create the bucket if it
    doesn't exist yet, then retry.
    """

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except S3Error as exc:
            if (
                exc.code == "NoSuchBucket"
                and settings.MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET
            ):
                log.warning(
                    b"Minio bucket '{self.bucket}' missing, trying to create it"
                )
                self.client.make_bucket(self.bucket)
                return fn(self, *args, **kwargs)
            raise

    return wrapper


class Minio:
    def __init__(self):
        endpoint = settings.MINIO_STORAGE_ENDPOINT
        access_key = settings.MINIO_STORAGE_ACCESS_KEY
        secret_key = settings.MINIO_STORAGE_SECRET_KEY
        secure = settings.MINIO_STORAGE_USE_HTTPS

        minio_http_client = None
        if settings.DEBUG and settings.MINIO_DISABLE_CERT_CHECKS:
            # This is a copy of what the minio client does internally,
            # just with the cert checking disabled.
            minio_http_client = urllib3.PoolManager(
                timeout=urllib3.Timeout.DEFAULT_TIMEOUT,
                maxsize=10,
                cert_reqs="CERT_NONE",
                ca_certs=None,
                retries=urllib3.Retry(
                    total=5, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504]
                ),
            )
        self.client = minio.Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            http_client=minio_http_client,
        )
        self.bucket = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME

    @_retry_on_missing_bucket
    def stat_object(self, object_name):
        """
        Get stat of object in bucket.

        :param object_name: str
        :return: stat response if successful, otherwise None
        """
        try:
            return self.client.stat_object(self.bucket, object_name)
        except S3Error as exc:
            log.error(f"Minio error, cannot stat object: {exc.code}")
            return None

    @_retry_on_missing_bucket
    def download_url(self, object_name):
        return self.client.presigned_get_object(
            self.bucket,
            object_name,
            timedelta(minutes=settings.MINIO_PRESIGNED_TTL_MINUTES),
        )

    @_retry_on_missing_bucket
    def upload_url(self, object_name):
        return self.client.presigned_put_object(
            self.bucket,
            object_name,
            timedelta(minutes=settings.MINIO_PRESIGNED_TTL_MINUTES),
        )

    @_retry_on_missing_bucket
    def remove_object(self, object_name):
        self.client.remove_object(self.bucket, object_name)

    @_retry_on_missing_bucket
    def copy_object(self, object_name, new_object_name):
        self.client.copy_object(
            self.bucket,
            new_object_name,
            CopySource(self.bucket, object_name),
        )

    @_retry_on_missing_bucket
    def move_object(self, object_name, new_object_name):
        self.copy_object(object_name, new_object_name)
        self.remove_object(object_name)


if settings.MEDIA_STORAGE_SERVICE == "minio":
    client = Minio()
else:  # pragma: no cover
    client = None
    raise NotImplementedError(
        f"Storage service {settings.MEDIA_STORAGE_SERVICE} is not implemented!"
    )
