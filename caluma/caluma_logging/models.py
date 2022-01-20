from django.db import models


class AccessLog(models.Model):
    OPERATIONS = [("query", "query"), ("mutation", "mutation")]

    timestamp = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    query = models.TextField()
    operation = models.CharField(choices=OPERATIONS, max_length=20)
    operation_name = models.CharField(max_length=100, blank=True, null=True)
    selection = models.CharField(max_length=100, blank=True, null=True)
    variables = models.JSONField(blank=True, null=True)
    status_code = models.PositiveIntegerField()
    has_error = models.BooleanField(default=False)
