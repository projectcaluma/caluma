import uuid
from functools import wraps

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models, transaction
from django.utils.functional import cached_property
from localized_fields.fields import LocalizedField, LocalizedTextField
from minio import S3Error
from simple_history.models import HistoricalRecords

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
    TYPE_FILE = "file"
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
        TYPE_FILE,
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
    def validate_on_enter(self):
        return self.configuration.get("validate_on_enter")

    @validate_on_enter.setter
    def validate_on_enter(self, value):
        self.configuration["validate_on_enter"] = value

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

        new_document = type(self).objects.create(
            form=self.form,
            meta=dict(self.meta),
            source=self,
            family=family,
            created_by_user=user.username if user else None,
            created_by_group=user.group if user else None,
            modified_by_user=user.username if user else None,
            modified_by_group=user.group if user else None,
        )
        if not family:
            family = new_document

        # copy answers
        for source_answer in self.answers.all():
            source_answer.copy(
                document_family=family, to_document=new_document, user=user
            )

        return new_document

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    file = models.OneToOneField(
        "File", on_delete=models.SET_NULL, null=True, blank=True
    )

    # override history to add extra fields on historical model
    history = HistoricalRecords(
        inherit=True,
        history_user_id_field=models.CharField(null=True, max_length=150),
        history_user_setter=core_models._history_user_setter,
        history_user_getter=core_models._history_user_getter,
        bases=[QuestionTypeHistoricalModel],
    )

    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete()
        super().delete(args, kwargs)

    def create_answer_documents(self, documents):
        family = getattr(self.document, "family", None)
        document_ids = [document.pk for document in documents]

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

    def unlink_unused_rows(self, docs_to_keep):
        existing = AnswerDocument.objects.filter(answer=self).exclude(
            document__in=docs_to_keep
        )
        for ans_doc in list(existing.select_related("document")):
            # Set document to be its own family
            # TODO: Can/should we delete the detached documents?
            ans_doc.document.set_family(ans_doc.document)
            ans_doc.delete()

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

        if self.question.type == Question.TYPE_FILE:
            new_answer.file = self.file.copy()
            new_answer.save()

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

    @_ignore_missing_file
    def _move_blob(self):
        # move the file on update
        # this makes sure it stays available when querying the history
        old_file = self.history.first()
        new_name = f"{old_file.pk}_{old_file.name}"
        client.move_object(self.object_name, new_name)

    @_ignore_missing_file
    def _copy(self, new_object_name):
        client.copy_object(self.object_name, new_object_name)

    def copy(self):
        copy = File.objects.create(name=self.name)
        self._copy(copy.object_name)
        return copy

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
