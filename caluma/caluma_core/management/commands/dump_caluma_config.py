import itertools

from django.apps import apps
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from django.db.models import Q


def get_form_filters(form_slugs):
    return {
        "caluma_form.Form": Q(pk__in=form_slugs),
        "caluma_form.Option": Q(questions__forms__pk__in=form_slugs),
        "caluma_form.Question": Q(forms__pk__in=form_slugs),
        "caluma_form.QuestionOption": Q(question__forms__pk__in=form_slugs),
        "caluma_form.FormQuestion": Q(form__pk__in=form_slugs),
        "caluma_form.Answer": Q(
            question__forms__pk__in=form_slugs, document__isnull=True
        ),
    }


class Command(BaseCommand):
    help = "Dump caluma objects. Currently supported: caluma_form.Form"

    def add_arguments(self, parser):
        parser.add_argument("args", nargs="*", help="Primary keys of given model")
        parser.add_argument(
            "--model", type=str, help="Model to dump, eg. 'caluma_form.Form'"
        )
        parser.add_argument(
            "--format",
            default="json",
            help="Specifies the output serialization format for fixtures.",
        )
        parser.add_argument(
            "--indent",
            type=int,
            default=2,
            help="Specifies the indent level to use when pretty-printing output.",
        )
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help="Nominates a specific database to dump fixtures from. "
            'Defaults to the "default" database.',
        )
        parser.add_argument(
            "-o", "--output", help="Specifies file to which the output is written."
        )

    def handle(self, *pks, **options):
        format = options["format"]
        indent = options["indent"]
        stream = open(options["output"], "w") if options["output"] else None

        if not pks:
            raise CommandError("Must provide primary keys")

        if format not in serializers.get_public_serializer_formats():
            try:
                serializers.get_serializer(format)
            except serializers.SerializerDoesNotExist:
                pass

            raise CommandError("Unknown serialization format: %s" % format)

        if not options.get("model"):
            raise CommandError("Missing `--model` option")

        app_label, model_label = options["model"].split(".")
        querysets = self.get_objects(pks)

        self.stdout.ending = None
        serializers.serialize(
            format,
            itertools.chain(*querysets),
            indent=indent,
            stream=stream or self.stdout,
        )

        if stream:
            stream.close()

    def get_objects(
        self, pks, app_label="caluma_form", model_label="Form", excluded_pks=None
    ):
        """Collect all objects including their "downwards" dependencies recursively."""

        querysets = []
        excluded_pks = excluded_pks or []
        sub_forms = []

        for model_identifier, model_filter in get_form_filters(pks).items():
            app_label, model_label = model_identifier.split(".")
            model = apps.get_model(app_label, model_label)

            qs = model.objects.filter(model_filter)
            querysets.append(qs)

            if model_label == "Question":
                sub_forms += qs.filter(row_form__isnull=False).values_list(
                    "row_form_id", flat=True
                )
                sub_forms += qs.filter(sub_form__isnull=False).values_list(
                    "sub_form_id", flat=True
                )

        if sub_forms:
            querysets += self.get_objects(set(sub_forms), excluded_pks=excluded_pks)

        return querysets
