from django.db.models import Q

from ..caluma_core.visibilities import BaseVisibility, filter_queryset_for
from ..caluma_form import models as form_models
from ..caluma_form.schema import Answer, Document
from . import models
from .schema import Case, WorkItem


class AddressedGroups(BaseVisibility):
    """Only show case, work item and document to addressed users through group."""

    def get_visible_work_items(self, node, queryset, info):
        groups = info.context.user.groups
        return models.WorkItem.objects.filter(addressed_groups__overlap=groups)

    def get_visible_cases(self, node, queryset, info):
        work_items = self.get_visible_work_items(node, queryset, info)
        cases = models.Case.objects.filter(
            Q(work_items__in=work_items) | Q(parent_work_item__in=work_items)
        )
        return cases

    def get_visible_documents(self, node, queryset, info):
        work_items = self.get_visible_work_items(node, queryset, info)
        cases = self.get_visible_cases(node, queryset, info)
        families = form_models.Document.objects.filter(
            Q(work_item__in=work_items) | Q(case__in=cases)
        ).values("family")
        return form_models.Document.objects.filter(family__in=families)

    @filter_queryset_for(WorkItem)
    def filter_querset_for_work_item(self, node, queryset, info):
        work_items = self.get_visible_work_items(node, queryset, info)
        return queryset.filter(pk__in=work_items)

    @filter_queryset_for(Case)
    def filter_queryset_for_case(self, node, queryset, info):
        cases = self.get_visible_cases(node, queryset, info)
        return queryset.filter(pk__in=cases)

    @filter_queryset_for(Document)
    def filter_queryset_for_document(self, node, queryset, info):
        documents = self.get_visible_documents(node, queryset, info)
        return queryset.filter(pk__in=documents)

    @filter_queryset_for(Answer)
    def filter_queryset_for_answer(self, node, queryset, info):
        documents = self.get_visible_documents(node, queryset, info)
        return queryset.filter(document__in=documents)
