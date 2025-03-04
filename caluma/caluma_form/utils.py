from logging import getLogger

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
        deps = set(question.calc_dependents)
        if question.slug in to_add:
            deps.add(slug)
        else:
            deps.remove(slug)
        question.calc_dependents = list(deps)
        question.save()


def recalculate_field(
    calc_field: structure.ValueField, update_recursively: bool = True
):
    """Recalculate the given value field and store the new answer.

    If it's not a calculated field, nothing happens.
    """
    if calc_field.question.type != models.Question.TYPE_CALCULATED_FLOAT:
        # Not a calc field - skip
        return  # pragma: no cover

    value = calc_field.calculate()

    answer, _ = models.Answer.objects.update_or_create(
        question=calc_field.question,
        document=calc_field.parent._document,
        defaults={"value": value},
    )
    # also save new answer to structure for reuse
    calc_field.refresh(answer)
    if update_recursively:
        recalculate_dependent_fields(calc_field, update_recursively)


def recalculate_dependent_fields(
    changed_field: structure.ValueField, update_recursively: bool = True
):
    """Update any calculated dependencies of the given field.

    If `update_recursively=False` is passed, no subsequent calc dependencies
    are updated (left to the caller in that case).
    """
    for dep_slug in changed_field.question.calc_dependents:
        dep_field = changed_field.get_field(dep_slug)
        if not dep_field:  # pragma: no cover
            # Calculated field is not in our form structure, which is
            # absolutely valid and OK
            continue
        recalculate_field(dep_field, update_recursively)


def update_or_create_calc_answer(question, document, update_dependents=True):
    """Recalculate all answers in the document after calc dependency change."""

    root = validators.DocumentValidator().get_validation_context(document.family)
    for field in root.find_all_fields_by_slug(question.slug):
        recalculate_field(field, update_recursively=update_dependents)
