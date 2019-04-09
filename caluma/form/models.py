from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.signals import post_init
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from localized_fields.fields import LocalizedField

from ..core.models import SlugModel, UUIDModel
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
    TYPE_DATE = "date"
    TYPE_CHOICE = "choice"
    TYPE_TEXTAREA = "textarea"
    TYPE_TEXT = "text"
    TYPE_TABLE = "table"
    TYPE_FORM = "form"
    TYPE_FILE = "file"

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
        help_text="Form that represents rows of a TableQuestion",
    )
    sub_form = models.ForeignKey(
        Form,
        blank=True,
        null=True,
        related_name="+",
        help_text="Form referenced in a FormQuestion",
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
        """Create a document (including child documents) for a given task."""
        if task.form_id is not None:
            doc = Document.objects.create(
                form_id=task.form_id,
                created_by_user=user.username,
                created_by_group=user.group,
            )
            self.create_and_link_child_documents(task.form, doc)
            return doc

        return None

    def create_and_link_child_documents(self, form, document):
        """Create child documents for all FormQuestions in the given form."""
        form_questions = form.questions.filter(type=Question.TYPE_FORM)

        for form_question in form_questions:
            child_document = self.create(form=form_question.sub_form)
            Answer.objects.create(
                question=form_question, document=document, value_document=child_document
            )
            self.create_and_link_child_documents(form_question.sub_form, child_document)


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
    value = JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)
    meta = JSONField(default=dict)
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="answers"
    )
    value_document = models.ForeignKey(
        Document,
        on_delete=models.DO_NOTHING,
        related_name="parent_answers",
        blank=True,
        null=True,
    )
    documents = models.ManyToManyField(
        Document, through="AnswerDocument", related_name="+"
    )
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


class File(UUIDModel):
    name = models.CharField(max_length=255)

    def delete(self, *args, **kwargs):
        client.remove_object(self.object_name)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # remove the file on update
        if self.created_at:
            client.remove_object(self.object_name)
        super().save(*args, **kwargs)

    @property
    def object_name(self):
        return f"{self.pk}_{slugify(self.name)}"

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
        ordering = ("-sort",)
        unique_together = ("answer", "document")
