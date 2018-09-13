from django.contrib.postgres.fields import JSONField
from django.db import models
from graphql.error import GraphQLError
from localized_fields.fields import LocalizedField

from caluma.models import BaseModel


class Form(BaseModel):
    slug = models.SlugField(max_length=50, primary_key=True)
    name = LocalizedField(blank=False, null=False, required=False)
    description = LocalizedField(blank=True, null=True, required=False)
    meta = JSONField(default={})
    is_published = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    questions = models.ManyToManyField(
        "Question", through="FormQuestion", related_name="forms"
    )

    def validate_editable(self):
        # TODO: Think of a more generic way to be implemented in graphene
        # https://github.com/graphql-python/graphene/issues/777
        if self.is_archived or self.is_published:
            raise GraphQLError(
                "Form %s may not be edited as it is archived or published" % self.pk
            )

    def __str__(self):
        return self.slug


class FormQuestion(BaseModel):
    form = models.ForeignKey("Form", on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    sort = models.PositiveIntegerField(editable=False, db_index=True, default=0)

    class Meta:
        ordering = ("-sort", "id")
        unique_together = ("form", "question")


class Question(BaseModel):
    # TODO: add descriptions
    TYPE_CHECKBOX = "checkbox"
    TYPE_INTEGER = "integer"
    TYPE_FLOAT = "float"
    TYPE_RADIO = "radio"
    TYPE_TEXTAREA = "textarea"
    TYPE_TEXT = "text"

    TYPE_CHOICES = (
        TYPE_CHECKBOX,
        TYPE_INTEGER,
        TYPE_FLOAT,
        TYPE_RADIO,
        TYPE_TEXTAREA,
        TYPE_TEXT,
    )
    TYPE_CHOICES_TUPLE = ((type_choice, type_choice) for type_choice in TYPE_CHOICES)

    slug = models.SlugField(max_length=50, primary_key=True)
    label = LocalizedField(blank=False, null=False, required=False)
    type = models.CharField(choices=TYPE_CHOICES_TUPLE, max_length=10)
    is_required = models.TextField(default="false")
    is_hidden = models.TextField(default="false")
    is_archived = models.BooleanField(default=False)
    configuration = JSONField(default={})
    meta = JSONField(default={})

    def __str__(self):
        return self.slug
