import uuid

from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import models, transaction
from django.db.models.signals import post_init
from django.dispatch import receiver
from localized_fields.fields import LocalizedField, LocalizedTextField
from simple_history.models import HistoricalRecords

from ..caluma_core import models as core_models
from .storage_clients import client


class Form(core_models.SlugModel):
    name = LocalizedField(blank=False, null=False, required=False)
    description = LocalizedField(blank=True, null=True, required=False)
    meta = JSONField(default=dict)
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
    )
    TYPE_CHOICES_TUPLE = ((type_choice, type_choice) for type_choice in TYPE_CHOICES)

    label = LocalizedField(blank=False, null=False, required=False)
    type = models.CharField(choices=TYPE_CHOICES_TUPLE, max_length=23)
    is_required = models.TextField(default="false")
    is_hidden = models.TextField(default="false")
    is_archived = models.BooleanField(default=False)
    placeholder = LocalizedField(blank=True, null=True, required=False)
    info_text = LocalizedField(blank=True, null=True, required=False)
    static_content = LocalizedTextField(blank=True, null=True, required=False)
    configuration = JSONField(default=dict)
    meta = JSONField(default=dict)
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

    def empty_value(self):
        """Return empty value for this question type."""

        empties = {
            Question.TYPE_MULTIPLE_CHOICE: [],
            Question.TYPE_TABLE: [],
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE: [],
        }
        return empties.get(self.type, None)

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
    meta = JSONField(default=dict)
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
            return Document.objects.create(
                form_id=task.form_id,
                created_by_user=user.username,
                created_by_group=user.group,
            )


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
    meta = JSONField(default=dict)

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

    def copy(self, family=None):
        """Create a copy including all its answers."""

        new_document = type(self).objects.create(
            form=self.form, meta=dict(self.meta), source=self, family=family
        )
        if not family:
            family = new_document

        # copy answers
        for source_answer in self.answers.all():
            new_answer = new_document.answers.create(
                question=source_answer.question,
                value=source_answer.value,
                meta=dict(source_answer.meta),
                date=source_answer.date,
            )

            if source_answer.question.type == Question.TYPE_FILE:
                new_answer.file = source_answer.file.copy()
                new_answer.save()

            # TableAnswer: copy AnswerDocument too
            for answer_doc in AnswerDocument.objects.filter(answer=source_answer):
                new_doc = answer_doc.document.copy(family=family)

                AnswerDocument.objects.create(
                    answer=new_answer, document=new_doc, sort=answer_doc.sort
                )

        return new_document

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
    value = JSONField(null=True, blank=True)
    meta = JSONField(default=dict)
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="answers"
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

    class Meta:
        # a question may only be answerd once per document
        unique_together = ("document", "question")
        indexes = [models.Index(fields=["date"]), GinIndex(fields=["meta", "value"])]


class File(core_models.UUIDModel):
    name = models.CharField(max_length=255)

    def _move_blob(self):
        # move the file on update
        # this makes sure it stays available when querying the history
        old_file = self.history.first()
        new_name = f"{old_file.pk}_{old_file.name}"
        client.move_object(self.object_name, new_name)

    def copy(self, *args, **kwargs):
        copy = File.objects.create(name=self.name)
        client.copy_object(self.object_name, copy.object_name)
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
        return client.stat_object(self.object_name).__dict__


@receiver(post_init, sender=Document)
def set_document_family(sender, instance, **kwargs):
    """
    Ensure document has the family pointer set.

    This sets the document's family if not overruled or set already.
    The family will be in the corresponding mutations when a tree
    structure is created or restructured.
    """
    if instance.family_id is None:
        # can't use instance.set_family() here as the instance isn't
        # in DB yet, causing integrity errors
        instance.family = instance


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
