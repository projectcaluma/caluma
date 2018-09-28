import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models

from caluma.models import BaseModel


class Document(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TODO: add user field once authentication is implemented
    form_specification = models.ForeignKey(
        "form.FormSpecification", on_delete=models.DO_NOTHING, related_name="documents"
    )
    meta = JSONField(default={})


class Answer(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        "form.Question", on_delete=models.DO_NOTHING, related_name="answers"
    )
    value = JSONField()
    meta = JSONField(default={})
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="answers"
    )

    class Meta:
        # a question may only be answerd once per document
        unique_together = ("document", "question")
