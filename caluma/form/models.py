from django.contrib.postgres.fields import JSONField
from django.db import models


class Form(models.Model):
    slug = models.SlugField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    meta = JSONField()
