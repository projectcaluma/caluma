from django.core.management.base import BaseCommand, CommandError

from caluma.caluma_form.api import copy_form
from caluma.caluma_form.models import Form


class Command(BaseCommand):
    """Copy a form."""

    help = "Copy a form."

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            type=str,
            help="The slug of the form to copy.",
        )
        parser.add_argument(
            "--slug",
            "-s",
            dest="slug",
            type=str,
            required=True,
            help="The slug of the newly created form.",
        )
        parser.add_argument(
            "--name",
            "-n",
            dest="name",
            type=str,
            default="",
            help="The name of the newly created form.",
        )
        parser.add_argument(
            "--description",
            "-d",
            dest="description",
            type=str,
            default="",
            help="The description of the newly created form.",
        )
        parser.add_argument(
            "--is-published",
            "-p",
            dest="is_published",
            type=bool,
            default=False,
            help="Whether the newly created form is published.",
        )

    def handle(self, *args, **options):
        source_slug = options["source"]
        new_slug = options["slug"]

        try:
            source = Form.objects.get(pk=source_slug)
        except Form.DoesNotExist:
            raise CommandError(f"Form '{source_slug}' not found - can't copy")

        copy_form(
            source=source,
            slug=new_slug,
            name=options["name"],
            description=options["description"],
            is_published=options["is_published"],
        )

        self.stdout.write(f"Copied form '{source_slug}' to new form '{new_slug}'")
