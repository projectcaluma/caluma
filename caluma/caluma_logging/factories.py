from factory import Faker, django

from . import models


class AccessLogFactory(django.DjangoModelFactory):
    timestamp = None
    username = Faker("user_name")
    query = ""
    operation = "query"
    operation_name = None
    selection = None
    variables = None
    status_code = 200
    has_error = False

    class Meta:
        model = models.AccessLog
