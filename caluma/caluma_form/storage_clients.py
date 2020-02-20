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

    def stat_object(self, object_name):
        """
        Get stat of object in bucket.

        :param object_name: str
        :return: stat response if successful, otherwise None
        """
        try:
            return self.client.stat_object(self.bucket, object_name)
        except minio.error.NoSuchKey:  # pragma: no cover
            # object does not exist
            pass
        except minio.error.NoSuchBucket:  # pragma: no cover
            if settings.MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET:
                self.client.make_bucket(self.bucket)
                return self.stat_object(object_name)
        except minio.error.ResponseError:  # pragma: no cover
            pass

    def download_url(self, object_name):
        try:
            return self.client.presigned_get_object(
                self.bucket,
                object_name,
                timedelta(minutes=settings.MINIO_PRESIGNED_TTL_MINUTES),
            )
        except minio.error.NoSuchBucket:  # pragma: no cover
            if settings.MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET:
                self.client.make_bucket(self.bucket)
                return self.download_url(object_name)

    def upload_url(self, object_name):
        try:
            return self.client.presigned_put_object(
                self.bucket,
                object_name,
                timedelta(minutes=settings.MINIO_PRESIGNED_TTL_MINUTES),
            )
        except minio.error.NoSuchBucket:  # pragma: no cover
            if settings.MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET:
                self.client.make_bucket(self.bucket)
                return self.upload_url(object_name)

    def remove_object(self, object_name):
        self.client.remove_object(self.bucket, object_name)

    def copy_object(self, object_name, new_object_name):
        self.client.copy_object(
            self.bucket, new_object_name, f"/{self.bucket}/{object_name}"
        )

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
