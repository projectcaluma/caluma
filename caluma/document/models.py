from django.contrib.postgres.fields import JSONField
from django.db import models

from caluma.models import UUIDModel


class Document(UUIDModel):
    # TODO: add user field once authentication is implemented
    form = models.ForeignKey(
        "form.Form", on_delete=models.DO_NOTHING, related_name="documents"
    )
    meta = JSONField(default={})


class Answer(UUIDModel):
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
