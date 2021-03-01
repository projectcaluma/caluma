from django.conf import settings
from django.core.management.base import BaseCommand

from ...storage_clients import client


class Command(BaseCommand):
    """Create a bucket based on the config."""

    help = "Create a bucket based on the config."

    def handle(self, *args, **options):
        bucket_name = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME

        if client.client.bucket_exists(bucket_name):  # pragma: no cover
            self.stdout.write(f"Bucket: {bucket_name} already exists!")
        else:
            client.client.make_bucket(bucket_name)
            self.stdout.write(f"Created bucket: {bucket_name}")
