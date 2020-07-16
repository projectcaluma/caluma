from django.core.management.base import BaseCommand
from simple_history.models import registered_models

# Instances which are created at run-time, referencing config-time models
# eg. Answers are created at run-time by users and referencing Question
RELATED_HISTORICAL_MODELS = {
    "Answer": {"question__type__isnull": True},
    "Document": {"form__name__isnull": True},
    "DynamicOption": {"question__type__isnull": True},
}


class Command(BaseCommand):
    """Cleanup historical records."""

    help = "Cleanup historical records."

    def add_arguments(self, parser):
        parser.add_argument("--force", dest="force", default=False, action="store_true")
        parser.add_argument(
            "-d",
            "--dangling",
            dest="dangling",
            default=False,
            action="store_true",
            help=(
                "Remove records missing a related instance, e.g."
                "HistoricalAnswer missing the Question it relates to."
            ),
        )

    def handle(self, *args, **options):
        force = options["force"]
        dangling = options["dangling"]

        for model in registered_models.values():
            if dangling and model.__name__ in RELATED_HISTORICAL_MODELS:
                qs = model.history.filter(**RELATED_HISTORICAL_MODELS[model.__name__])
            else:
                qs = model.history.none()

            action_str = "Deleting" if force else "Would delete"
            self.stdout.write(
                f'{action_str} {qs.count()} historical records from model "{model.__name__}"'
            )
            if force:
                qs.delete()
