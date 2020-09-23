import dateparser
from django.core.management.base import BaseCommand
from django.utils import timezone

from caluma.caluma_logging.models import AccessLog


class Command(BaseCommand):
    """Cleanup access log."""

    help = "Cleanup access log."

    def add_arguments(self, parser):
        parser.add_argument("--force", dest="force", default=False, action="store_true")
        parser.add_argument(
            "-k",
            "--keep",
            dest="keep",
            default="2 weeks",
            help=(
                "Duration for which to keep the access log, older entries will be removed."
            ),
        )

    def handle(self, *args, **options):
        force = options["force"]
        keep = options["keep"]
        lt = dateparser.parse(options["keep"])

        if lt is not None:
            lt = timezone.make_aware(lt)

        entries = AccessLog.objects.filter(timestamp__lt=lt)

        self.stdout.write(
            f"Deleting {entries.count()} access log entries older than {keep}."
        )

        if force:
            entries.delete()
