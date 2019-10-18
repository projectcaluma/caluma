from dateparser import parse
from django.core.management.base import BaseCommand
from django.utils import timezone
from simple_history.models import registered_models


class Command(BaseCommand):
    """Cleanup historical records."""

    help = "Cleanup historical records."

    def add_arguments(self, parser):
        parser.add_argument("--force", dest="force", default=False, action="store_true")
        parser.add_argument(
            "-k",
            "--keep",
            dest="keep",
            default="1 year",
            help=(
                "Duration we want to keep the records. "
                "E.g. '6 months', '1 year'. Uses dateparser."
            ),
        )

    def handle(self, *args, **options):
        force = options["force"]

        lt = parse(options["keep"])
        if lt is not None:
            lt = timezone.make_aware(lt)

        for _, model in registered_models.items():
            qs = model.history.all()
            if lt is not None:
                qs = model.history.filter(history_date__lt=lt)

            action_str = "Deleting" if force else "Would delete"
            self.stdout.write(
                f'{action_str} {qs.count()} historical records from model "{model.__name__}"'
            )
            if force:
                qs.delete()
