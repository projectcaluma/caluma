# SPDX-FileCopyrightText: 2019 Adfinis SyGroup AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from dateparser import parse
from django.core.management.base import BaseCommand
from django.utils import timezone
from simple_history.models import registered_models


class Command(BaseCommand):
    """Cleanup historical records."""

    help = "Cleanup historical records."

    def add_arguments(self, parser):
        parser.add_argument("--dry", dest="dry", action="store_true")
        parser.add_argument(
            "-k",
            "--keep",
            dest="keep",
            default="",
            help=(
                "Duration we want to keep the records. "
                "E.g. '6 months', '1 year'. Uses dateparser."
            ),
        )

    def handle(self, *args, **options):
        lt = parse(options["keep"])
        if lt is not None:
            lt = timezone.make_aware(lt)

        for _, model in registered_models.items():
            qs = model.history.all()
            if lt is not None:
                qs = model.history.filter(history_date__lt=lt)

            action_str = "Would delete"
            if not options["dry"]:
                action_str = "Deleting"
            self.stdout.write(
                f'{action_str} {qs.count()} historical records from model "{model.__name__}"'
            )
            if not options["dry"]:
                qs.delete()
