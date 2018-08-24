from django.contrib.postgres.fields import JSONField
from django.db import models


class Form(models.Model):
    slug = models.SlugField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    meta = JSONField(default={})
    is_published = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    # TODO: ManyToMany questions


class Question(models.Model):
    TYPE_CHECKBOX = "checkbox"
    TYPE_NUMBER = "number"
    TYPE_RADIO = "radio"
    TYPE_TEXTAREA = "textarea"
    TYPE_TEXT = "text"

    TYPE_CHOICES = (TYPE_CHECKBOX, TYPE_NUMBER, TYPE_RADIO, TYPE_TEXTAREA, TYPE_TEXT)
    TYPE_CHOICES_TUPLE = ((type_choice, type_choice) for type_choice in TYPE_CHOICES)

    slug = models.SlugField(max_length=50, primary_key=True)
    label = models.CharField(max_length=255)
    type = models.CharField(choices=TYPE_CHOICES_TUPLE, max_length=10)
    is_required = models.TextField()
    is_hidden = models.TextField()
    is_archived = models.BooleanField(default=False)
    configuration = JSONField(default={})
    meta = JSONField(default={})
