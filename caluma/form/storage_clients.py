from datetime import timedelta

import minio
from django.conf import settings


class Minio:
    def __init__(self):
        endpoint = settings.MINIO_STORAGE_ENDPOINT
        access_key = settings.MINIO_STORAGE_ACCESS_KEY
        secret_key = settings.MINIO_STORAGE_SECRET_KEY
        secure = settings.MINIO_STORAGE_USE_HTTPS
        self.client = minio.Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )
        self.bucket = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME

    def bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                if settings.MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET:
                    self.client.make_bucket(self.bucket)
                    return True
                return False
        except minio.error.ResponseError:  # pragma: no cover
            return False
        return True

    def object_exists(self, object_name):
        if not self.bucket_exists():
            return False

        try:
            self.client.stat_object(self.bucket, object_name)
        except minio.error.NoSuchKey:  # pragma: no cover
            # object does not exist
            return False
        except minio.error.NoSuchBucket:  # pragma: no cover
            # should really not happen. Handled anyway...
            return False
        except minio.error.ResponseError:  # pragma: no cover
            return False
        return True

    def download_url(self, object_name):
        if self.object_exists(object_name):
            return self.client.presigned_get_object(
                self.bucket,
                object_name,
                timedelta(minutes=settings.MINIO_PRESIGNED_TTL_MINUTES),
            )

    def upload_url(self, object_name):
        if self.bucket_exists():
            return self.client.presigned_put_object(
                self.bucket,
                object_name,
                timedelta(minutes=settings.MINIO_PRESIGNED_TTL_MINUTES),
            )

    def remove_object(self, object_name):
        self.client.remove_object(self.bucket, object_name)


if settings.MEDIA_STORAGE_SERVICE == "minio":
    client = Minio()
else:  # pragma: no cover
    client = None
    raise NotImplementedError(
        f"Storage service {settings.MEDIA_STORAGE_SERVICE} is not implemented!"
    )
