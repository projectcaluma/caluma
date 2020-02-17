from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import models, transaction
from django.db.models.signals import post_init
from django.dispatch import receiver
from localized_fields.fields import LocalizedField, LocalizedTextField

from ..caluma_core.models import NaturalKeyModel, SlugModel, UUIDModel
from .storage_clients import client


class Form(SlugModel):
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


class FormQuestion(NaturalKeyModel):
    form = models.ForeignKey("Form", on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    sort = models.PositiveIntegerField(editable=False, db_index=True, default=0)

    def natural_key(self):
        return f"{self.form_id}.{self.question_id}"

    class Meta:
        ordering = ["-sort"]
        unique_together = ("form", "question")


class Question(SlugModel):
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


class QuestionOption(NaturalKeyModel):
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    option = models.ForeignKey("Option", on_delete=models.CASCADE)
    sort = models.PositiveIntegerField(editable=False, db_index=True, default=0)

    def natural_key(self):
        return f"{self.question_id}.{self.option_id}"

    class Meta:
        ordering = ["-sort"]
        unique_together = ("option", "question")


class Option(SlugModel):
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


class Document(UUIDModel):
    objects = DocumentManager()

    family = models.UUIDField(
        help_text="Family id which document belongs too.", db_index=True
    )
    form = models.ForeignKey(
        "caluma_form.Form", on_delete=models.DO_NOTHING, related_name="documents"
    )
    meta = JSONField(default=dict)

    class Meta:
        indexes = [GinIndex(fields=["meta"])]


class Answer(UUIDModel):
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

    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete()
        super().delete(args, kwargs)

    class Meta:
        # a question may only be answerd once per document
        unique_together = ("document", "question")
        indexes = [models.Index(fields=["date"]), GinIndex(fields=["meta", "value"])]


class File(UUIDModel):
    name = models.CharField(max_length=255)

    def _move_blob(self):
        # move the file on update
        # this makes sure it stays available when querying the history
        old_file = self.history.first()
        new_name = f"{old_file.pk}_{old_file.name}"
        client.move_object(self.object_name, new_name)

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
    Family id is inherited from document id.

    Family will be manually set on mutation where a tree structure
    is created.
    """
    if instance.family is None:
        instance.family = instance.pk


class AnswerDocument(UUIDModel):
    answer = models.ForeignKey("Answer", on_delete=models.CASCADE)
    document = models.ForeignKey("Document", on_delete=models.CASCADE)
    sort = models.PositiveIntegerField(editable=False, db_index=True, default=0)

    class Meta:
        ordering = ["-sort"]
        unique_together = ("answer", "document")


class DynamicOption(UUIDModel):
    slug = models.CharField(max_length=255)
    label = LocalizedField(blank=False, null=False, required=False)
    document = models.ForeignKey("Document", on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("slug", "document", "question")
