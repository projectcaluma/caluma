from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_init
from django.dispatch import receiver
from localized_fields.fields import LocalizedField

from ..core.models import SlugModel, UUIDModel


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
    )


class FormQuestion(UUIDModel):
    form = models.ForeignKey("Form", on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    sort = models.PositiveIntegerField(editable=False, db_index=True, default=0)

    class Meta:
        ordering = ("-sort",)
        unique_together = ("form", "question")


class Question(SlugModel):
    TYPE_MULTIPLE_CHOICE = "multiple_choice"
    TYPE_INTEGER = "integer"
    TYPE_FLOAT = "float"
    TYPE_CHOICE = "choice"
    TYPE_TEXTAREA = "textarea"
    TYPE_TEXT = "text"
    TYPE_TABLE = "table"

    TYPE_CHOICES = (
        TYPE_MULTIPLE_CHOICE,
        TYPE_INTEGER,
        TYPE_FLOAT,
        TYPE_CHOICE,
        TYPE_TEXTAREA,
        TYPE_TEXT,
        TYPE_TABLE,
    )
    TYPE_CHOICES_TUPLE = ((type_choice, type_choice) for type_choice in TYPE_CHOICES)

    label = LocalizedField(blank=False, null=False, required=False)
    type = models.CharField(choices=TYPE_CHOICES_TUPLE, max_length=15)
    is_required = models.TextField(default="false")
    is_hidden = models.TextField(default="false")
    is_archived = models.BooleanField(default=False)
    configuration = JSONField(default=dict)
    meta = JSONField(default=dict)
    options = models.ManyToManyField(
        "Option", through="QuestionOption", related_name="questions"
    )
    row_form = models.ForeignKey(
        Form,
        blank=True,
        null=True,
        related_name="+",
        help_text="One row of table is represented by this form",
    )

    source = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="+",
        help_text="Reference this question has been copied from",
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


class QuestionOption(UUIDModel):
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    option = models.ForeignKey("Option", on_delete=models.CASCADE)
    sort = models.PositiveIntegerField(editable=False, db_index=True, default=0)

    class Meta:
        ordering = ("-sort",)
        unique_together = ("option", "question")


class Option(SlugModel):
    label = LocalizedField(blank=False, null=False, required=False)
    meta = JSONField(default=dict)
    source = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="+",
        help_text="Reference this option has been copied from",
    )


class DocumentManager(models.Manager):
    def create_document_for_task(self, task, user):
        if task.form_id is not None:
            return Document.objects.create(
                form_id=task.form_id,
                created_by_user=user.username,
                created_by_group=user.group,
            )

        return None


class Document(UUIDModel):
    objects = DocumentManager()

    family = models.UUIDField(
        help_text="Family id which document belongs too.", db_index=True
    )
    form = models.ForeignKey(
        "form.Form", on_delete=models.DO_NOTHING, related_name="documents"
    )
    meta = JSONField(default=dict)


class Answer(UUIDModel):
    question = models.ForeignKey(
        "form.Question", on_delete=models.DO_NOTHING, related_name="answers"
    )
    value = JSONField(null=True, blank=True)
    meta = JSONField(default=dict)
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="answers"
    )
    documents = models.ManyToManyField(
        Document, through="AnswerDocument", related_name="+"
    )

    class Meta:
        # a question may only be answerd once per document
        unique_together = ("document", "question")


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
        ordering = ("-sort",)
        unique_together = ("answer", "document")
