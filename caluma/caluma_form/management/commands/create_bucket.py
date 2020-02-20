from django.conf import settings
from django.core.management.base import BaseCommand
from minio.error import BucketAlreadyExists, BucketAlreadyOwnedByYou, ResponseError

from ...storage_clients import client


class Command(BaseCommand):
    """Create a bucket based on the config."""

    help = "Create a bucket based on the config."

    def handle(self, *args, **options):
        bucket_name = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME

        try:
            client.client.make_bucket(bucket_name)
        except BucketAlreadyOwnedByYou:  # pragma: no cover
            self.stderr.write(f"Bucket: {bucket_name} is already owned by you!")
        except BucketAlreadyExists:  # pragma: no cover
            self.stderr.write(f"Bucket: {bucket_name} already exists!")
        except ResponseError:  # pragma: no cover
            raise
        else:
            self.stdout.write(f"Created bucket: {bucket_name}")
