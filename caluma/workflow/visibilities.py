from django.db.models import Q

from . import models
from ..core.visibilities import BaseVisibility, filter_queryset_for
from ..form.schema import Document
from .schema import Case, WorkItem


class AddressedGroups(BaseVisibility):
    """Only show case, work item and document to addressed users through group."""

    def _get_visibile_work_items(self, node, queryset, info):
        groups = info.context.user.groups
        return models.WorkItem.objects.filter(addressed_groups__overlap=groups)

    def _get_visible_cases(self, node, queryset, info):
        work_items = self._get_visibile_work_items(node, queryset, info)
        cases = models.Case.objects.filter(
            Q(work_items__in=work_items) | Q(parent_work_item__in=work_items)
        )
        return cases

    @filter_queryset_for(WorkItem)
    def filter_querset_for_work_item(self, node, queryset, info):
        work_items = self._get_visibile_work_items(node, queryset, info)
        return queryset.filter(pk__in=work_items)

    @filter_queryset_for(Case)
    def filter_queryset_for_case(self, node, queryset, info):
        cases = self._get_visible_cases(node, queryset, info)
        return queryset.filter(pk__in=cases)

    @filter_queryset_for(Document)
    def filter_queryset_for_document(self, node, queryset, info):
        work_items = self._get_visibile_work_items(node, queryset, info)
        cases = self._get_visible_cases(node, queryset, info)
        return queryset.filter(Q(work_item__in=work_items) | Q(case__in=cases))
