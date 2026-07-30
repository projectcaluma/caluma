import time
from collections import defaultdict
from graphlib import TopologicalSorter
from logging import getLogger
from typing import Self

from caluma.caluma_form import models, structure, validators
from caluma.caluma_form.jexl import QuestionJexl

log = getLogger(__name__)


def update_calc_dependents(slug, old_expr, new_expr):
    """Update the calc_dependents lists of our calc *dependencies*.

    The given (old and new) expressions are analyzed to see which
    questions are referenced in "our" calc question. Then, those
    questions' calc_dependents list is updated, such that it correctly
    represents the new situation.

    Example: If our expression newly contains the question `foo`, then the
    `foo` question needs to know about it (we add "our" slug to the `foo`s
    calc dependents)
    """
    jexl = QuestionJexl(field=None)
    old_q = set(
        list(jexl.extract_referenced_questions(old_expr))
        + list(jexl.extract_referenced_mapby_questions(old_expr))
    )
    new_q = set(
        list(jexl.extract_referenced_questions(new_expr))
        + list(jexl.extract_referenced_mapby_questions(new_expr))
    )

    to_add = new_q - old_q
    to_remove = old_q - new_q

    questions = models.Question.objects.filter(pk__in=list(to_add | to_remove))

    for question in questions:
        if question.slug in to_add:
            if slug not in question.calc_dependents:
                question.calc_dependents.append(slug)
                question.save()
        elif slug in question.calc_dependents:
            question.calc_dependents.remove(slug)
            question.save()


def recalculate_and_update_dependents(calc_field: structure.ValueField):
    """Recalculate the given value field and store the new answer.

    If it's not a calculated field, nothing happens.
    """
    if calc_field.question.type != models.Question.TYPE_CALCULATED_FLOAT:
        return  # pragma: no cover

    did_update = recalculate_field(calc_field)
    if did_update:
        recalculate_dependent_fields(calc_field)


def recalculate_field(calc_field: structure.ValueField) -> bool:
    """Recalculate the given value field and store the new answer.

    If it's not a calculated field, nothing happens.

    Unless you know what you're doing, you should probably use
    `recalculate_and_update_dependents()` instead, as this variant
    will not update any dependents of the calculated field.

    Return True if an update happened, False otherwise.
    For non-calculated fields, True is returned to ensure dependents are not culled.
    """
    if calc_field.question.type != models.Question.TYPE_CALCULATED_FLOAT:
        # Not a calc field - skip
        return True

    start = time.time()

    old_value = calc_field.get_value()
    value = calc_field.calculate()

    did_change = value != old_value

    if did_change or not calc_field.answer:
        # If the value changed, or we have no answer for the calc
        # question: update the value
        answer, _ = models.Answer.objects.update_or_create(
            question=calc_field.question,
            document=calc_field.parent._document,
            defaults={"value": value},
        )

        # no need to refresh recursive - all subsequent dependents will be
        # explicitly recalculated anyway, so we won't need to hit the DB
        # and refresh them here (repeatedly)
        calc_field.refresh(answer, recursive=False)
    duration = time.time() - start

    status = "updated value" if did_change else "did not change value"
    log.debug(
        "Recalculation(%s): took %1.3fs, %s", calc_field.get_path(), duration, status
    )

    return did_change


class DependencyList(list):
    def __init__(self, *changed_fields: structure.BaseField) -> Self:
        """
        Build a list of fields that need to be recalculated if the given field changes.

        The list is collected in a way such that an iterative recalculation will
        implicitly be correct, as the fields that need previous values are sorted
        later in the list.
        """

        if not changed_fields:  # pragma: no cover
            # Nothing to do
            return

        # field-id -> list[field-id] mapping
        self._reasons: defaultdict[id, list[id]] = defaultdict(list)

        self.struc = changed_fields[0].get_root()
        self._roots = {id(f) for f in changed_fields}

        assert all(f.get_root() is self.struc for f in changed_fields), (
            "DependencyList can only deal with fields of the same structure"
        )

        dependencies = defaultdict(list)

        # need a lookup table of id->field, as TopologicalSorter needs dict,
        # and we can't hash the fields directly. So we're using their object IDs
        # instead and translate between them
        self._fields_by_id = {}

        for field in changed_fields:
            self._collect_field_deps(field, dependencies)

        ts = TopologicalSorter(dependencies)

        # TopologicalSorter expects the adjacency_list the "other way around", i.e.
        # for every node the incoming nodes should be given. To account for this, we
        # just reverse the resulting order.
        id_queue = list(reversed(list(ts.static_order())))

        # Fill the dependency list so our users can then run the recalculation
        self.extend(self._fields_by_id[field_id] for field_id in id_queue)

        # Store the reasons for the particular ordering
        for field_id, dependents in dependencies.items():
            for dep in dependents:
                self._reasons[dep].append(field_id)

    def _collect_field_deps(self, field, dependencies):
        field_id = id(field)

        if field_id in self._fields_by_id:
            # Happens if it's already been collected via another path.
            # Does not need to be collected anymore
            return
        self._fields_by_id[field_id] = field

        # Ensure the field is registered in the dependency graph, even if it has no
        # dependents. Required for TopologicalSorter to include it in the sort.
        dependencies.setdefault(field_id, [])

        for dep_slug in field.question.calc_dependents:
            for dep_field in self.struc.find_all_fields_by_slug(dep_slug):
                dep_field_id = id(dep_field)
                dependencies[field_id].append(dep_field_id)

                self._collect_field_deps(dep_field, dependencies)

        if isinstance(field, (structure.RowSet, structure.FieldSet)):
            # if the changed field is a document or rowset, we need
            # to recalculate everything that depends on it's children
            # as well
            for child in field.children():
                self._collect_field_deps(child, dependencies)

    def remove_reason_for(
        self, field: structure.ValueField, to_remove: structure.ValueField
    ):
        """
        Remove the given reason for recalculation from the given field.

        If the reason for recalculation (the to_remove field) didn't change,
        then that field is not a reason for recalculation anymore, and
        recalculation might be skipped
        """
        self._reasons[id(field)].remove(id(to_remove))

    def get_reason_for(self, field: structure.BaseField) -> list[structure.ValueField]:
        """Return a list of fields that are the reason this given field needs recalc."""
        reason_ids = self._reasons[id(field)]
        return [self._fields_by_id[field_id] for field_id in reason_ids]

    def perform_recalculation(self, allow_culling=True, recalculate_roots=True):
        """Recalculate all fields in the associated structure.

        If allow_culling is set to False, the "culling" optimisation is disabled:
        It will stop recalculation if all inputs of a calculated question didn't change.

        If recalculate_roots is set to False, the fields that were used to initialize
        this DependencyList will not be recalculated. This is useful if they have
        been recalculated already.
        """
        for field in self:
            log.debug("Recalculating %s", field.get_path())
            is_root = id(field) in self._roots
            if (
                allow_culling
                and not is_root
                and not self.get_reason_for(field)
                and field.answer
            ):
                # There is no reason (anymore) to recalculate this field,
                # as none of the recalculations of the dependencies have changed
                # their value
                continue

            if is_root and not recalculate_roots:
                did_update = True
            else:
                did_update = recalculate_field(field)

            if allow_culling and not did_update:
                for dep_slug in field.question.calc_dependents:
                    # remove field from reason that dep_slug needs to be recalculated
                    dep_fields = self.struc.find_all_fields_by_slug(dep_slug)
                    for dep_field in dep_fields:
                        self.remove_reason_for(dep_field, field)


def recalculate_dependent_fields(
    *changed_fields: structure.BaseField, recalculate_roots: bool = False
):
    """Update any calculated dependencies of the given fields.

    Iterate over all dependents, recursively, and recalculate them
    in an optimized fashion.

    :param changed_fields: The fields that have changed and trigger recalculation.
    :param recalculate_roots: Whether to also recalculate the given changed_fields.
    """
    if not changed_fields:
        return  # pragma: no cover

    update_list = DependencyList(*changed_fields)
    update_list.perform_recalculation(recalculate_roots=recalculate_roots)


def recalculate_all_calc_fields(struc):
    """Fully recalculate all the structure's calculated fields.

    Go through all calculated fields of the structure and update them
    in an efficient manner.
    """
    calculated_fields = (
        field
        for field in struc.get_all_fields()
        if field.question.type == models.Question.TYPE_CALCULATED_FLOAT
    )
    DependencyList(*calculated_fields).perform_recalculation()


def update_or_create_calc_answer(question, document):
    """Recalculate all answers in the document after calc dependency change."""

    root = validators.DocumentValidator().get_validation_context(document.family)
    fields_to_recalc = root.find_all_fields_by_slug(question.slug)
    dependencies_to_recalc = DependencyList(*fields_to_recalc)

    dependencies_to_recalc.perform_recalculation(allow_culling=False)
