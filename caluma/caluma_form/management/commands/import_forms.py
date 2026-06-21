from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from caluma.caluma_form import api, models


@dataclass
class NormalizedOption:
    slug: str
    label: str | dict
    is_hidden: str
    meta: dict
    line: str


@dataclass
class NormalizedQuestion:
    slug: str
    label: str | dict
    type: str
    is_required: str
    is_hidden: str
    meta: dict
    configuration: dict
    placeholder: str | dict | None
    hint_text: str | dict | None
    info_text: str | dict | None
    row_form: str | None
    sub_form: str | None
    options: list[NormalizedOption]
    line: str


@dataclass
class NormalizedForm:
    slug: str
    name: str | dict
    description: str | dict
    meta: dict
    is_published: bool
    is_archived: bool
    questions: list[NormalizedQuestion]
    line: str


class Command(BaseCommand):
    help = "Import forms, questions, and options from a YAML scaffold file."

    def add_arguments(self, parser):
        parser.add_argument("path", type=str, help="Path to YAML import file")
        parser.add_argument(
            "--update",
            action="store_true",
            help="Allow updating already existing entities",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate input and references without writing to the database",
        )
        parser.add_argument(
            "--language",
            type=str,
            default=None,
            help="Language code used when plain strings are provided for localized fields",
        )

    def handle(self, *args, **options):
        payload = self._load_yaml(options["path"])
        forms = self._normalize(payload, default_language=options["language"])
        self._validate_duplicates(forms)
        self._validate_references(forms)

        existing_forms, existing_questions, existing_options = self._collect_existing(
            forms
        )
        self._assert_conflicts(
            existing_forms,
            existing_questions,
            existing_options,
            allow_update=options["update"],
        )

        if options["dry_run"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Dry-run successful: {len(forms)} forms, "
                    f"{sum(len(form.questions) for form in forms)} questions"
                )
            )
            return

        stats = self._import(
            forms,
            existing_forms=existing_forms,
            existing_questions=existing_questions,
            existing_options=existing_options,
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Import finished: "
                f"forms created={stats['forms_created']} updated={stats['forms_updated']}, "
                f"questions created={stats['questions_created']} updated={stats['questions_updated']}, "
                f"options created={stats['options_created']} updated={stats['options_updated']}, "
                f"form-questions synced={stats['form_questions_synced']}, "
                f"question-options synced={stats['question_options_synced']}"
            )
        )

    def _load_yaml(self, path):
        file_path = Path(path)
        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}
        except yaml.YAMLError as exc:
            raise CommandError(f"Failed to parse YAML: {exc}") from exc

        if not isinstance(data, dict):
            raise CommandError("YAML root must be an object")
        if "forms" not in data:
            raise CommandError("YAML root must contain 'forms'")

        return data

    def _normalize(self, payload, default_language):
        self._assert_allowed_keys(payload, {"forms", "language"}, "root")
        file_language = payload.get("language")
        if file_language is not None and not isinstance(file_language, str):
            raise CommandError("root.language must be a string")

        effective_language = default_language or file_language
        forms = payload["forms"]
        if not isinstance(forms, list):
            raise CommandError("'forms' must be a list")

        return [
            self._normalize_form(form_data, index, effective_language)
            for index, form_data in enumerate(forms)
        ]

    def _normalize_form(self, data, index, default_language):
        if not isinstance(data, dict):
            raise CommandError(f"forms[{index}] must be an object")

        self._assert_allowed_keys(
            data,
            {
                "slug",
                "label",
                "name",
                "description",
                "meta",
                "is_published",
                "is_archived",
                "questions",
            },
            f"forms[{index}]",
        )

        name = data.get("name", data.get("label"))
        if name is None:
            raise CommandError(
                f"forms[{index}] requires 'name' or 'label' to derive form name"
            )

        slug = data.get("slug") or self._slug_from_value(name)
        if not slug:
            raise CommandError(f"forms[{index}] produced empty slug")

        questions_data = data.get("questions", [])
        if not isinstance(questions_data, list):
            raise CommandError(f"forms[{index}].questions must be a list")

        normalized_questions = [
            self._normalize_question(
                question_data,
                form_index=index,
                question_index=question_index,
                default_language=default_language,
            )
            for question_index, question_data in enumerate(questions_data)
        ]

        return NormalizedForm(
            slug=slug,
            name=self._localized(name, default_language),
            description=self._localized(data.get("description", ""), default_language),
            meta=self._normalize_dict(data.get("meta", {}), f"forms[{index}].meta"),
            is_published=bool(data.get("is_published", False)),
            is_archived=bool(data.get("is_archived", False)),
            questions=normalized_questions,
            line=f"forms[{index}]",
        )

    def _normalize_question(self, data, form_index, question_index, default_language):
        path = f"forms[{form_index}].questions[{question_index}]"
        if not isinstance(data, dict):
            raise CommandError(f"{path} must be an object")

        self._assert_allowed_keys(
            data,
            {
                "slug",
                "label",
                "type",
                "required",
                "is_required",
                "is_hidden",
                "placeholder",
                "hint_text",
                "info_text",
                "meta",
                "configuration",
                "row_form",
                "sub_form",
                "options",
                "static_content",
            },
            path,
        )

        label = data.get("label")
        if label is None:
            raise CommandError(f"{path} requires 'label'")

        question_type = self._normalize_question_type(data, path)
        slug = data.get("slug") or self._slug_from_value(label)
        if not slug:
            raise CommandError(f"{path} produced empty slug")

        is_required = self._normalize_required(data, path)
        is_hidden = self._normalize_jexl_bool(
            data.get("is_hidden", "false"), path, "is_hidden"
        )

        options_data = self._normalize_options_data(data.get("options", []), path)
        self._validate_question_consistency(
            question_type=question_type,
            options_data=options_data,
            row_form=data.get("row_form"),
            sub_form=data.get("sub_form"),
            path=path,
        )

        normalized_options = [
            self._normalize_option(
                option_data=option_data,
                question_slug=slug,
                path=f"{path}.options[{option_index}]",
                default_language=default_language,
            )
            for option_index, option_data in enumerate(options_data)
        ]

        return NormalizedQuestion(
            slug=slug,
            label=self._localized(label, default_language),
            type=question_type,
            is_required=is_required,
            is_hidden=is_hidden,
            meta=self._normalize_dict(data.get("meta", {}), f"{path}.meta"),
            configuration=self._normalize_dict(
                data.get("configuration", {}),
                f"{path}.configuration",
            ),
            placeholder=self._localized(data["placeholder"], default_language)
            if "placeholder" in data
            else None,
            hint_text=self._localized(data["hint_text"], default_language)
            if "hint_text" in data
            else None,
            info_text=self._localized(data["info_text"], default_language)
            if "info_text" in data
            else None,
            row_form=data.get("row_form"),
            sub_form=data.get("sub_form"),
            options=normalized_options,
            line=path,
        )

    def _normalize_question_type(self, data, path):
        question_type = data.get("type")
        if question_type is None:
            return (
                models.Question.TYPE_CHOICE
                if "options" in data
                else models.Question.TYPE_TEXT
            )

        if question_type not in models.Question.TYPE_CHOICES:
            raise CommandError(f"{path}.type '{question_type}' is invalid")

        return question_type

    def _normalize_required(self, data, path):
        if "required" in data and "is_required" in data:
            raise CommandError(
                f"{path} must not define both 'required' and 'is_required'"
            )

        if "is_required" in data:
            value = data["is_required"]
        else:
            value = bool(data.get("required", False))

        return self._normalize_jexl_bool(value, path, "is_required")

    def _normalize_options_data(self, options_data, path):
        if not isinstance(options_data, list):
            raise CommandError(f"{path}.options must be a list")

        return options_data

    def _validate_question_consistency(
        self,
        *,
        question_type,
        options_data,
        row_form,
        sub_form,
        path,
    ):
        choice_types = {
            models.Question.TYPE_CHOICE,
            models.Question.TYPE_MULTIPLE_CHOICE,
        }
        if options_data and question_type not in choice_types:
            raise CommandError(
                f"{path}.options are only valid for '{models.Question.TYPE_CHOICE}' "
                f"or '{models.Question.TYPE_MULTIPLE_CHOICE}' questions"
            )
        if question_type in choice_types and not options_data:
            raise CommandError(
                f"{path}.options must not be empty for '{question_type}' questions"
            )

        if question_type == models.Question.TYPE_TABLE and not row_form:
            raise CommandError(f"{path}.row_form is required for table questions")

        if question_type == models.Question.TYPE_FORM and not sub_form:
            raise CommandError(f"{path}.sub_form is required for form questions")

    def _normalize_option(self, option_data, question_slug, path, default_language):
        if isinstance(option_data, str):
            label = option_data
            slug = None
            is_hidden = "false"
            meta = {}
        elif isinstance(option_data, dict):
            self._assert_allowed_keys(
                option_data,
                {"slug", "label", "is_hidden", "meta"},
                path,
            )
            label = option_data.get("label")
            if label is None:
                raise CommandError(f"{path}.label is required")
            slug = option_data.get("slug")
            is_hidden = option_data.get("is_hidden", "false")
            meta = self._normalize_dict(option_data.get("meta", {}), f"{path}.meta")
        else:
            raise CommandError(f"{path} must be string or object")

        normalized_is_hidden = self._normalize_jexl_bool(is_hidden, path, "is_hidden")

        generated_slug = self._slug_from_value(label)
        if not generated_slug:
            raise CommandError(f"{path} produced empty option slug")

        return NormalizedOption(
            slug=slug or f"{question_slug}-{generated_slug}",
            label=self._localized(label, default_language),
            is_hidden=normalized_is_hidden,
            meta=meta,
            line=path,
        )

    def _validate_duplicates(self, forms):
        form_counter = Counter(form.slug for form in forms)
        self._raise_if_duplicates(form_counter, "form")

        question_counter = Counter(
            question.slug for form in forms for question in form.questions
        )
        self._raise_if_duplicates(question_counter, "question")

        option_counter = Counter(
            option.slug
            for form in forms
            for question in form.questions
            for option in question.options
        )
        self._raise_if_duplicates(option_counter, "option")

    def _validate_references(self, forms):
        references = {
            question.row_form
            for form in forms
            for question in form.questions
            if question.row_form
        }
        references.update(
            question.sub_form
            for form in forms
            for question in form.questions
            if question.sub_form
        )

        imported_form_slugs = {form.slug for form in forms}
        persisted_form_slugs = set(
            models.Form.objects.filter(slug__in=references).values_list(
                "slug", flat=True
            )
        )
        known_form_slugs = imported_form_slugs | persisted_form_slugs

        for form in forms:
            for question in form.questions:
                if (
                    question.type == models.Question.TYPE_TABLE
                    and question.row_form not in known_form_slugs
                ):
                    raise CommandError(
                        f"{question.line}.row_form '{question.row_form}' is unknown"
                    )
                if (
                    question.type == models.Question.TYPE_FORM
                    and question.sub_form not in known_form_slugs
                ):
                    raise CommandError(
                        f"{question.line}.sub_form '{question.sub_form}' is unknown"
                    )

    def _collect_existing(self, forms):
        form_slugs = [form.slug for form in forms]
        question_slugs = [q.slug for form in forms for q in form.questions]
        option_slugs = [
            option.slug
            for form in forms
            for question in form.questions
            for option in question.options
        ]

        existing_forms = {
            form.slug: form for form in models.Form.objects.filter(slug__in=form_slugs)
        }
        existing_questions = {
            question.slug: question
            for question in models.Question.objects.filter(slug__in=question_slugs)
        }
        existing_options = {
            option.slug: option
            for option in models.Option.objects.filter(slug__in=option_slugs)
        }

        return existing_forms, existing_questions, existing_options

    def _assert_conflicts(
        self,
        existing_forms,
        existing_questions,
        existing_options,
        *,
        allow_update,
    ):
        if allow_update:
            return

        if existing_forms:
            slug = sorted(existing_forms.keys())[0]
            raise CommandError(f"Form '{slug}' already exists")
        if existing_questions:
            slug = sorted(existing_questions.keys())[0]
            raise CommandError(f"Question '{slug}' already exists")
        if existing_options:
            slug = sorted(existing_options.keys())[0]
            raise CommandError(f"Option '{slug}' already exists")

    @transaction.atomic
    def _import(self, forms, *, existing_forms, existing_questions, existing_options):
        stats = {
            "forms_created": 0,
            "forms_updated": 0,
            "questions_created": 0,
            "questions_updated": 0,
            "options_created": 0,
            "options_updated": 0,
            "form_questions_synced": 0,
            "question_options_synced": 0,
        }

        persisted_forms = self._persist_forms(forms, existing_forms, stats)
        persisted_questions = self._persist_questions_and_options(
            forms,
            persisted_forms,
            existing_questions,
            existing_options,
            stats,
        )
        self._sync_form_questions(forms, persisted_forms, persisted_questions, stats)

        return stats

    def _persist_forms(self, forms, existing_forms, stats):
        persisted_forms = {}
        for form in forms:
            existing_form = existing_forms.get(form.slug)
            saved_form = api.save_form(
                slug=form.slug,
                name=form.name,
                description=form.description,
                meta=form.meta,
                is_published=form.is_published,
                is_archived=form.is_archived,
                form=existing_form,
            )
            persisted_forms[form.slug] = saved_form
            stats["forms_updated" if existing_form else "forms_created"] += 1

        return persisted_forms

    def _persist_questions_and_options(
        self,
        forms,
        persisted_forms,
        existing_questions,
        existing_options,
        stats,
    ):
        persisted_questions = {}

        for form in forms:
            for question in form.questions:
                existing_question = existing_questions.get(question.slug)
                saved_question = api.save_question(
                    slug=question.slug,
                    label=question.label,
                    type=question.type,
                    is_required=question.is_required,
                    is_hidden=question.is_hidden,
                    placeholder=question.placeholder,
                    hint_text=question.hint_text,
                    info_text=question.info_text,
                    meta=question.meta,
                    configuration=question.configuration,
                    row_form=persisted_forms.get(question.row_form),
                    sub_form=persisted_forms.get(question.sub_form),
                    question=existing_question,
                )
                persisted_questions[question.slug] = saved_question
                stats[
                    "questions_updated" if existing_question else "questions_created"
                ] += 1

                if question.options:
                    self._persist_options_for_question(
                        question,
                        saved_question,
                        existing_options,
                        stats,
                    )

        return persisted_questions

    def _persist_options_for_question(
        self, question, saved_question, existing_options, stats
    ):
        persisted_options = []
        for option in question.options:
            existing_option = existing_options.get(option.slug)
            saved_option = api.save_option(
                slug=option.slug,
                label=option.label,
                is_hidden=option.is_hidden,
                meta=option.meta,
                option=existing_option,
            )
            persisted_options.append(saved_option)
            stats["options_updated" if existing_option else "options_created"] += 1
            existing_options[option.slug] = saved_option

        api.save_question_options(saved_question, persisted_options)
        stats["question_options_synced"] += 1

    def _sync_form_questions(self, forms, persisted_forms, persisted_questions, stats):
        for form in forms:
            api.save_form_questions(
                persisted_forms[form.slug],
                [persisted_questions[q.slug] for q in form.questions],
            )
            stats["form_questions_synced"] += 1

    def _normalize_jexl_bool(self, value, path, key):
        if isinstance(value, bool):
            return "true" if value else "false"
        if not isinstance(value, str):
            raise CommandError(f"{path}.{key} must be a string or boolean")
        return value

    def _normalize_dict(self, value, path):
        if not isinstance(value, dict):
            raise CommandError(f"{path} must be an object")
        return value

    def _assert_allowed_keys(self, data, allowed, path):
        unknown = sorted(set(data.keys()) - set(allowed))
        if unknown:
            raise CommandError(
                f"{path} contains unsupported keys: {', '.join(unknown)}"
            )

    def _raise_if_duplicates(self, counter, entity):
        duplicates = sorted(slug for slug, count in counter.items() if count > 1)
        if duplicates:
            raise CommandError(f"Duplicate {entity} slug(s): {', '.join(duplicates)}")

    def _slug_from_value(self, value: Any) -> str:
        if isinstance(value, dict):
            for candidate in value.values():
                if candidate:
                    result = slugify(candidate)
                    if result:
                        return result
            return ""

        return slugify(value)

    def _localized(self, value, default_language):
        if isinstance(value, dict):
            return value
        if default_language:
            return {default_language: value}
        return value
