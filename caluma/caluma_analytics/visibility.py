from caluma.caluma_form import models as form_models, schema as form_schema
from caluma.caluma_workflow import schema as workflow_schema

from . import sql


def qs_method_factory(node_cls, model_cls=None):
    if not model_cls:
        model_cls = node_cls._meta.model

    def method(self):
        queryset = model_cls.objects.all()
        if not self.is_disabled:
            queryset = node_cls.get_queryset(queryset, self.info)
        return sql.Query.from_queryset(queryset)

    method.__doc__ = f"""
    Return an analytics Query object for {model_cls.__name__}.

    The query object contains CTE representing the visibility rules
    as defined in Caluma's settings for {model_cls.__name__}.
    """

    return method


class CalumaVisibilitySource:
    def __init__(self, info, is_disabled):
        self.info = info
        self.is_disabled = is_disabled

    cases = qs_method_factory(workflow_schema.Case)
    work_items = qs_method_factory(workflow_schema.WorkItem)
    documents = qs_method_factory(form_schema.Document)
    answers = qs_method_factory(form_schema.Answer, form_models.Answer)
