from functools import wraps

import uuid_extensions
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models, transaction
from django.utils.functional import cached_property
from localized_fields.fields import LocalizedField, LocalizedTextField
from minio import S3Error
from simple_history.models import HistoricalRecords

from caluma.caluma_data_source.data_source_handlers import get_data_sources

from ..caluma_core import models as core_models
from .storage_clients import client


class Form(core_models.SlugModel):
    name = LocalizedField(blank=False, null=False, required=False)
    description = LocalizedField(blank=True, null=True, required=False)
    meta = models.JSONField(default=dict)
    is_published = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    questions = models.ManyToManyField(
        "Question", through="FormQuestion", related_name="forms"
    )
    source = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        help_text="Reference this form has been copied from",
        related_name="+",
        on_delete=models.SET_NULL,
    )

    @classmethod
    def _get_all_raw_forms(cls, forms: list):
        return cls.objects.raw(
            """
            WITH RECURSIVE
                forms(slug) AS (
                    SELECT slug
                    FROM caluma_form_form
                    WHERE slug = ANY (%s)
                    UNION ALL
                    SELECT
                        all_subforms.subform_id AS slug
                    FROM forms JOIN all_subforms ON (all_subforms.form_id = forms.slug )
                ),
                all_subforms(form_id, subform_id) AS (
                    SELECT
                        caluma_form_formquestion.form_id,
                        COALESCE(caluma_form_question.row_form_id, caluma_form_question.sub_form_id) AS subform_id
                    FROM caluma_form_formquestion
                    JOIN caluma_form_question ON (caluma_form_formquestion.question_id = caluma_form_question.slug)
                    WHERE caluma_form_question.type IN ('form', 'table')
                )
            SELECT * FROM forms;
        """,
            [forms],
        )

    @classmethod
    def get_all_forms(cls, forms: list):  # pragma: no cover
        return Form.objects.filter(pk__in=cls._get_all_raw_forms(forms))

    @classmethod
    def get_all_questions(cls, forms: list):
        return Question.objects.filter(forms__in=cls._get_all_raw_forms(forms))

    class Meta:
        indexes = [GinIndex(fields=["meta"])]


class FormQuestion(core_models.NaturalKeyModel):
    form = models.ForeignKey("Form", on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    sort = models.PositiveIntegerField(editable=False, db_index=True, default=0)

    def natural_key(self):
        return f"{self.form_id}.{self.question_id}"

    class Meta:
        ordering = ["-sort"]
        unique_together = ("form", "question")


class Question(core_models.SlugModel):
    TYPE_MULTIPLE_CHOICE = "multiple_choice"
    TYPE_INTEGER = "integer"
    TYPE_FLOAT = "float"
    TYPE_DATE = "date"
    TYPE_CHOICE = "choice"
    TYPE_TEXTAREA = "textarea"
    TYPE_TEXT = "text"
    TYPE_TABLE = "table"
    TYPE_FORM = "form"
    TYPE_FILES = "files"
    TYPE_DYNAMIC_CHOICE = "dynamic_choice"
    TYPE_DYNAMIC_MULTIPLE_CHOICE = "dynamic_multiple_choice"
    TYPE_STATIC = "static"
    TYPE_CALCULATED_FLOAT = "calculated_float"
    TYPE_ACTION_BUTTON = "action_button"

    TYPE_CHOICES = (
        TYPE_MULTIPLE_CHOICE,
        TYPE_INTEGER,
        TYPE_FLOAT,
        TYPE_DATE,
        TYPE_CHOICE,
        TYPE_TEXTAREA,
        TYPE_TEXT,
        TYPE_TABLE,
        TYPE_FORM,
        TYPE_FILES,
        TYPE_DYNAMIC_CHOICE,
        TYPE_DYNAMIC_MULTIPLE_CHOICE,
        TYPE_STATIC,
        TYPE_CALCULATED_FLOAT,
        TYPE_ACTION_BUTTON,
    )
    TYPE_CHOICES_TUPLE = [(type_choice, type_choice) for type_choice in TYPE_CHOICES]

    ACTION_COMPLETE = "complete"
    ACTION_SKIP = "skip"
    ACTION_CHOICES = (
        ACTION_COMPLETE,
        ACTION_SKIP,
    )

    COLOR_PRIMARY = "primary"
    COLOR_SECONDARY = "secondary"
    COLOR_DEFAULT = "default"
    COLOR_CHOICES = (
        COLOR_PRIMARY,
        COLOR_SECONDARY,
        COLOR_DEFAULT,
    )

    label = LocalizedField(blank=False, null=False, required=False)
    type = models.CharField(choices=TYPE_CHOICES_TUPLE, max_length=23)
    is_required = models.TextField(default="false")
    is_hidden = models.TextField(default="false")
    is_archived = models.BooleanField(default=False)
    placeholder = LocalizedField(blank=True, null=True, required=False)
    info_text = LocalizedField(blank=True, null=True, required=False)
    hint_text = LocalizedField(blank=True, null=True, required=False)
    static_content = LocalizedTextField(blank=True, null=True, required=False)
    configuration = models.JSONField(default=dict)
    meta = models.JSONField(default=dict)
    data_source = models.CharField(max_length=255, blank=True, null=True)
    options = models.ManyToManyField(
        "Option", through="QuestionOption", related_name="questions"
    )
    row_form = models.ForeignKey(
        Form,
        blank=True,
        null=True,
        related_name="+",
        help_text="Form that represents rows of a TableQuestion",
        on_delete=models.PROTECT,
    )
    sub_form = models.ForeignKey(
        Form,
        blank=True,
        null=True,
        related_name="+",
        help_text="Form referenced in a FormQuestion",
        on_delete=models.PROTECT,
    )

    source = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="+",
        help_text="Reference this question has been copied from",
        on_delete=models.SET_NULL,
    )
    format_validators = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )

    default_answer = models.OneToOneField(
        "Answer", on_delete=models.SET_NULL, related_name="+", null=True, blank=True
    )

    calc_expression = models.TextField(null=True, blank=True)
    calc_dependents = ArrayField(
        models.CharField(max_length=255, blank=True), default=list
    )

    @property
    def min_length(self):
        return self.configuration.get("min_length")

    @min_length.setter
    def min_length(self, value):
        self.configuration["min_length"] = value

    @property
    def max_length(self):
        return self.configuration.get("max_length")

    @max_length.setter
    def max_length(self, value):
        self.configuration["max_length"] = value

    @property
    def max_value(self):
        return self.configuration.get("max_value")

    @max_value.setter
    def max_value(self, value):
        self.configuration["max_value"] = value

    @property
    def min_value(self):
        return self.configuration.get("min_value")

    @min_value.setter
    def min_value(self, value):
        self.configuration["min_value"] = value

    @property
    def action(self):
        return self.configuration.get("action")

    @action.setter
    def action(self, value):
        self.configuration["action"] = value

    @property
    def color(self):
        return self.configuration.get("color")

    @color.setter
    def color(self, value):
        self.configuration["color"] = value

    @property
    def step(self):
        return self.configuration.get("step")

    @step.setter
    def step(self, value):
        self.configuration["step"] = value

    @property
    def validate_on_enter(self):
        return self.configuration.get("validate_on_enter")

    @validate_on_enter.setter
    def validate_on_enter(self, value):
        self.configuration["validate_on_enter"] = value

    @property
    def show_validation(self):
        return self.configuration.get("show_validation")

    @show_validation.setter
    def show_validation(self, value):
        self.configuration["show_validation"] = value

    def empty_value(self):
        """Return empty value for this question type."""

        empties = {
            Question.TYPE_MULTIPLE_CHOICE: [],
            Question.TYPE_TABLE: [],
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE: [],
        }
        return empties.get(self.type, None)

    def __repr__(self):
        base = super().__repr__()
        return base[:-1] + f", type={self.type})"

    class Meta:
        indexes = [GinIndex(fields=["meta"])]


class QuestionOption(core_models.NaturalKeyModel):
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    option = models.ForeignKey("Option", on_delete=models.CASCADE)
    sort = models.PositiveIntegerField(editable=False, db_index=True, default=0)

    def natural_key(self):
        return f"{self.question_id}.{self.option_id}"

    class Meta:
        ordering = ["-sort"]
        unique_together = ("option", "question")


class Option(core_models.SlugModel):
    label = LocalizedField(blank=False, null=False, required=False)
    is_hidden = models.TextField(default="false")
    is_archived = models.BooleanField(default=False)
    meta = models.JSONField(default=dict)
    source = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="+",
        help_text="Reference this option has been copied from",
        on_delete=models.SET_NULL,
    )

    class Meta:
        indexes = [GinIndex(fields=["meta"])]


class DocumentManager(models.Manager):
    @transaction.atomic
    def create_document_for_task(self, task, user):
        """Create a document for a given task."""
        if task.form_id is not None:
            # import domain logic here, in order to avoid recursive import error
            from .domain_logic import SaveDocumentLogic

            return SaveDocumentLogic.create({"form": task.form}, user=user)


class Document(core_models.UUIDModel):
    objects = DocumentManager()

    family = models.ForeignKey(
        "self",
        help_text="Family id which document belongs too.",
        null=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    form = models.ForeignKey(
        "caluma_form.Form", on_delete=models.DO_NOTHING, related_name="documents"
    )
    source = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        help_text="Reference this document has been copied from",
        related_name="copies",
        on_delete=models.SET_NULL,
    )
    meta = models.JSONField(default=dict)

    def flat_answer_map(self):
        """
        Return a dictionary with the flattened answer map for this document.

        The keys are the question IDs, and the values are either the answer value
        or date for non-table questions, or a list of flattened answer maps for
        table questions.

        Example usage:
        >>> doc = Document.objects.get(pk=1)
        >>> flat_map = doc.flat_answer_map()
        >>> print(flat_map)
        {
            "first-name": 'John',
            "second-name": 'Doe',
            "email-in-subform": 'john.doe@example.com',
            "projects": [
                {"title": 'Project A', "date": '2022-01-01'},
                {"title": 'Project B', "date": '2022-02-01'},
                {"title": 'Project C', "date": '2022-03-01'}
            ]
        }
        """
        answers = {}
        for answer in self.answers.all():
            if answer.question.type == Question.TYPE_TABLE:
                answers[answer.question_id] = [
                    answer.flat_answer_map() for answer in answer.documents.all()
                ]
            else:
                answers[answer.question_id] = answer.value or answer.date

        return answers

    def set_family(self, root_doc):
        """Set the family to the given root_doc.

        Apply the same to all row documents within this document,
        recursively.
        """
        if self.family != root_doc:
            self.family = root_doc
            self.save()

        table_answers = Answer.objects.filter(
            document=self,
            # TODO this is not REALLY required, as only table answers
            # have child documents anyhow. Leaving it out would avoid
            # a JOIN to the question table
            question__type=Question.TYPE_TABLE,
        )

        child_documents = AnswerDocument.objects.filter(
            answer__in=table_answers
        ).select_related("document")

        for answer_document in child_documents:
            answer_document.document.set_family(root_doc)

    def copy(self, family=None, user=None):
        """Create a copy including all its answers."""

        # no need to update calculated questions, since calculated answers
        # are copied as well
        meta = dict(self.meta)
        meta["_defer_calculation"] = True

        new_document = type(self).objects.create(
            form=self.form,
            meta=meta,
            source=self,
            family=family,
            created_by_user=user.username if user else None,
            created_by_group=user.group if user else None,
            modified_by_user=user.username if user else None,
            modified_by_group=user.group if user else None,
        )

        is_main_doc = False
        if not family:
            is_main_doc = True
            family = new_document

        for source_answer in self.answers.all():
            source_answer.copy(
                document_family=family, to_document=new_document, user=user
            )

        new_document.meta.pop("_defer_calculation", None)
        new_document.save()

        if is_main_doc:
            self._update_dynamic_answers_after_copy(family)

        return new_document

    def _update_dynamic_answers_after_copy(self, family):
        """Update all dynamic answers of the document family.

        when the main doc is completely copied, this means all nested documents and
        answers have been copied as well. Fetch all answers of the document family
        and update the dynamic options of the answers through the data source on_copy
        method.
        """

        # get all dynamic answers of the document family
        family_dynamic_answers = Answer.objects.filter(
            document__in=Document.objects.filter(family=family).values_list(
                "pk", flat=True
            ),
            question__type__in=[
                Question.TYPE_DYNAMIC_CHOICE,
                Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            ],
        )

        for new_answer in family_dynamic_answers:
            answer_value_changed = False

            # initialize the data source used by the dynamic question
            data_source_class = get_data_sources(dic=True)[
                new_answer.question.data_source
            ]
            data_source = data_source_class()

            for new_dynamic_option in DynamicOption.objects.filter(
                document=new_answer.document, question=new_answer.question
            ):
                # get the old answer from the source document for comparison
                old_answer = Answer.objects.get(
                    document=new_answer.document.source,
                    question=new_answer.question,
                )

                # let the data source decide what to do with the answer value.
                new_slug, new_label = data_source.on_copy(
                    old_answer=old_answer,
                    new_answer=new_answer,
                    old_value=(new_dynamic_option.slug, new_dynamic_option.label),
                )

                # modify the answer value if the datasource decides to change or
                # discard the answer value.
                if new_slug is None or new_slug != new_dynamic_option.slug:
                    answer_value_changed = True
                    new_answer.value = new_answer.modify_changed_choice_answer(
                        new_answer.question,
                        new_dynamic_option.slug,
                        new_slug,
                        new_answer.value,
                    )

                # update the dynamic option if the slug has changed
                if new_slug and new_slug != new_dynamic_option.slug:
                    new_dynamic_option.slug = new_slug
                    new_dynamic_option.label = new_label
                    new_dynamic_option.save()

                # delete the dynamic option if the slug is None
                elif not new_slug:
                    new_dynamic_option.delete()

            # save the answer value if changed after checking all dynamic options
            if answer_value_changed:
                new_answer.save(update_fields=["value"])

    @cached_property
    def last_modified_answer(self):
        """Get most recently modified answer of the document.

        For root documents, we want to look through the whole document, while
        for row documents only the table-local answer is wanted.
        """
        if self.family != self:
            answers = self.answers
        else:
            answers = Answer.objects.filter(document__family=self)

        return answers.order_by("-modified_at").first()

    @property
    def modified_content_at(self):
        return getattr(self.last_modified_answer, "modified_at", None)

    @property
    def modified_content_by_user(self):
        return getattr(self.last_modified_answer, "modified_by_user", None)

    @property
    def modified_content_by_group(self):
        return getattr(self.last_modified_answer, "modified_by_group", None)

    def __repr__(self):
        return f"Document(form={self.form!r})"

    class Meta:
        indexes = [GinIndex(fields=["meta"])]


class QuestionTypeHistoricalModel(models.Model):
    """Extra fields for HistoricalAnswer."""

    history_question_type = models.CharField(
        choices=Question.TYPE_CHOICES_TUPLE, max_length=23
    )

    class Meta:
        abstract = True


class Answer(core_models.BaseModel):
    """Records an answer to a question of arbitrary type."""

    # We need to replicate the UUIDModel in order to register it as historical model.
    # Otherwise simple_history complains that the model is already registered,
    id = models.UUIDField(
        primary_key=True, default=uuid_extensions.uuid7, editable=False
    )
    question = models.ForeignKey(
        "caluma_form.Question", on_delete=models.DO_NOTHING, related_name="answers"
    )
    value = models.JSONField(null=True, blank=True)
    meta = models.JSONField(default=dict)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="answers",
        null=True,
        blank=True,
    )
    documents = models.ManyToManyField(
        Document, through="AnswerDocument", related_name="+"
    )
    date = models.DateField(null=True, blank=True)

    # override history to add extra fields on historical model
    history = HistoricalRecords(
        inherit=True,
        history_user_id_field=models.CharField(null=True, max_length=150),
        history_user_setter=core_models._history_user_setter,
        history_user_getter=core_models._history_user_getter,
        bases=[QuestionTypeHistoricalModel],
    )

    def delete(self, *args, **kwargs):
        # Files need to be deleted in sequence (not via on_delete)
        # so the deletion code on the storage is properly triggered
        for file in self.files.all():
            file.delete()
        super().delete(args, kwargs)

    def create_answer_documents(self, documents):
        """Create AnswerDocuments for this table question, and attach them.

        Return a dict with two keys: "created", and "updated", each
        containing a list of document IDs that were either created or kept.
        """
        family = getattr(self.document, "family", None)
        document_ids = [document.pk for document in documents]
        res = {"updated": [], "created": []}

        for sort, document_id in enumerate(reversed(document_ids), start=1):
            ans_doc, created = AnswerDocument.objects.get_or_create(
                answer=self, document_id=document_id, defaults={"sort": sort}
            )
            if not created and ans_doc.sort != sort:
                ans_doc.sort = sort
                ans_doc.save()
            if created:
                # Already-existing documents are already in the family,
                # so we're updating only the newly attached rows
                ans_doc.document.set_family(family)
                res["created"].append(document_id)
            else:
                res["updated"].append(document_id)
        return res

    def unlink_unused_rows(self, docs_to_keep):
        existing = AnswerDocument.objects.filter(answer=self).exclude(
            document__in=docs_to_keep
        )
        for ans_doc in list(existing.select_related("document")):
            # Set document to be its own family
            # TODO: Can/should we delete the detached documents?
            ans_doc.document.set_family(ans_doc.document)
            ans_doc.delete()

    def modify_changed_choice_answer(self, question, old_slug, new_slug, answer_value):
        """Handle answer value updates based on the datasource on_copy decision.

        For single dynamic choice questions:
        - The value will be changed to None for discard operations (None will be the
            value of new_slug)
        - The value will be changed to the new slug for change operations
        - The value will remain unchanged for retain operations

        For multiple dynamic choice questions:
        - The slug will be removed from the list for discard operations
        - The slug will be replaced in the list with the new slug for change operations
        - The list will remain unchanged for retain operations

        """
        if question.type == Question.TYPE_DYNAMIC_CHOICE:
            return new_slug if answer_value == old_slug else answer_value

        if question.type == Question.TYPE_DYNAMIC_MULTIPLE_CHOICE:
            # don't modify the answer if it has no value
            if not answer_value:
                return answer_value

            if old_slug in answer_value:
                if new_slug is None:
                    answer_value.remove(old_slug)
                else:
                    answer_value[answer_value.index(old_slug)] = new_slug

        return answer_value

    def copy(self, document_family=None, to_document=None, user=None):
        new_answer, _ = type(self).objects.update_or_create(
            question=self.question,
            document=to_document,
            defaults={
                "value": self.value,
                "meta": dict(self.meta),
                "date": self.date,
                "created_by_user": user.username if user else None,
                "created_by_group": user.group if user else None,
                "modified_by_user": user.username if user else None,
                "modified_by_group": user.group if user else None,
            },
        )

        if self.question.type == Question.TYPE_FILES:
            for file in self.files.all():
                file.copy(to_answer=new_answer)

        if self.question.type in [
            Question.TYPE_DYNAMIC_CHOICE,
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
        ]:
            for dynamic_option in DynamicOption.objects.filter(
                document=self.document, question=self.question
            ):
                DynamicOption.objects.update_or_create(
                    document=to_document,
                    question=dynamic_option.question,
                    slug=dynamic_option.slug,
                    defaults={
                        "label": dynamic_option.label,
                        "created_by_user": user.username if user else None,
                        "created_by_group": user.group if user else None,
                    },
                )

        # TableAnswer: copy AnswerDocument too
        for answer_doc in AnswerDocument.objects.filter(answer=self):
            new_doc = answer_doc.document.copy(family=document_family, user=user)

            AnswerDocument.objects.create(
                answer=new_answer,
                document=new_doc,
                sort=answer_doc.sort,
                created_by_user=user.username if user else None,
                created_by_group=user.group if user else None,
                modified_by_user=user.username if user else None,
                modified_by_group=user.group if user else None,
            )
        return new_answer

    @property
    def selected_options(self):
        map = {
            Question.TYPE_CHOICE: (Option, {"slug": self.value}),
            Question.TYPE_MULTIPLE_CHOICE: (Option, {"slug__in": self.value}),
            Question.TYPE_DYNAMIC_CHOICE: (
                DynamicOption,
                {
                    "slug": self.value,
                    "question": self.question,
                    "document": self.document,
                },
            ),
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE: (
                DynamicOption,
                {
                    "slug__in": self.value,
                    "question": self.question,
                    "document": self.document,
                },
            ),
        }

        if self.question.type not in map:
            return None

        if not self.value:
            return []

        model, filters = map[self.question.type]
        queryset = model.objects.filter(**filters)

        def index_from_value(obj):
            return self.value.index(obj.slug)

        # Keep the same order as the value
        return sorted(queryset, key=index_from_value)

    def __repr__(self):
        return f"Answer(document={self.document!r}, question={self.question!r}, value={self.value!r})"

    class Meta:
        # a question may only be answerd once per document
        unique_together = ("document", "question")
        indexes = [models.Index(fields=["date"]), GinIndex(fields=["meta", "value"])]


def _ignore_missing_file(fn):
    """Ignore errors due to missing file.

    If no file is uploaded to the storage service, we want to ignore the resulting
    exceptions in order to still be able to modify/delete the File.
    """

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except S3Error as exc:
            if exc.code == "NoSuchKey":
                return
            raise

    return wrapper


class File(core_models.UUIDModel):
    name = models.CharField(max_length=255)

    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name="files", null=True, default=None
    )

    @_ignore_missing_file
    def _move_blob(self):
        # move the file on update
        # this makes sure it stays available when querying the history
        old_file = self.history.first()
        if not old_file:  # pragma: no cover
            # No history - cannot move object to preserve history.
            return
        new_name = f"{old_file.pk}_{old_file.name}"
        client.move_object(self.object_name, new_name)

    @_ignore_missing_file
    def _copy(self, new_object_name):
        client.copy_object(self.object_name, new_object_name)

    def copy(self, to_answer):
        copy = File.objects.create(name=self.name, answer=to_answer or self.answer)
        self._copy(copy.object_name)
        return copy

    def rename(self, new_name):
        from_object_name = self.object_name
        self.name = new_name
        client.move_object(from_object_name, self.object_name)

    def delete(self, *args, **kwargs):
        self._move_blob()
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.created_at:
            self._move_blob()
        super().save(*args, **kwargs)

    @property
    def object_name(self):
        return f"{self.pk}_{self.name}"

    @property
    def upload_url(self):
        return client.upload_url(self.object_name)

    @property
    def download_url(self):
        return client.download_url(self.object_name)

    @property
    def metadata(self):
        stat = client.stat_object(self.object_name)
        if not stat:
            # This could happen if no file was uploaded, but the client
            # still requests the property
            return None
        return {
            # There are some more metadata values, but we're
            # not showing everything here. Most of the remaining
            # stuff is not set, or not useful for clients anyway
            "bucket_name": stat.bucket_name,
            "content_type": stat.content_type,
            "etag": stat.etag,
            "last_modified": stat.last_modified.isoformat(),
            "metadata": dict(stat.metadata),
            "size": stat.size,
        }


class AnswerDocument(core_models.UUIDModel):
    answer = models.ForeignKey("Answer", on_delete=models.CASCADE)
    document = models.ForeignKey("Document", on_delete=models.CASCADE)
    sort = models.PositiveIntegerField(editable=False, db_index=True, default=0)

    class Meta:
        ordering = ["-sort"]
        unique_together = ("answer", "document")


class DynamicOption(core_models.UUIDModel):
    slug = models.CharField(max_length=255)
    label = LocalizedField(blank=False, null=False, required=False)
    document = models.ForeignKey("Document", on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("slug", "document", "question")
