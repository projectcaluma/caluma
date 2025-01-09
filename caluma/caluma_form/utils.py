from django.db.models import Prefetch

from caluma.caluma_form import models, structure
from caluma.caluma_form.jexl import QuestionJexl


def prefetch_document(document_id):
    """Fetch a document while prefetching the entire structure.

    This is needed to reduce the query count when almost all the form data
    is needed for a given document, e.g. when recalculating calculated
    answers: in order to evaluate calc expressions the complete document
    structure is needed, which would otherwise result in a lot of queries.
    """
    return (
        models.Document.objects.filter(pk=document_id)
        .prefetch_related(*_build_document_prefetch_statements(prefetch_options=True))
        .first()
    )


def _build_document_prefetch_statements(prefix="", prefetch_options=False):
    question_queryset = models.Question.objects.select_related(
        "sub_form", "row_form"
    ).order_by("-formquestion__sort")

    if prefetch_options:
        question_queryset = question_queryset.prefetch_related(
            Prefetch(
                "options",
                queryset=models.Option.objects.order_by("-questionoption__sort"),
            )
        )

    if prefix:  # pragma: no cover
        prefix += "__"

    return [
        f"{prefix}answers",
        f"{prefix}dynamicoption_set",
        Prefetch(
            f"{prefix}answers__answerdocument_set",
            queryset=models.AnswerDocument.objects.select_related(
                "document__form", "document__family"
            )
            .prefetch_related("document__answers", "document__form__questions")
            .order_by("-sort"),
        ),
        Prefetch(
            # root form -> questions
            f"{prefix}form__questions",
            queryset=question_queryset.prefetch_related(
                Prefetch(
                    # root form -> row forms -> questions
                    "row_form__questions",
                    queryset=question_queryset,
                ),
                Prefetch(
                    # root form -> sub forms -> questions
                    "sub_form__questions",
                    queryset=question_queryset.prefetch_related(
                        Prefetch(
                            # root form -> sub forms -> row forms -> questions
                            "row_form__questions",
                            queryset=question_queryset,
                        ),
                        Prefetch(
                            # root form -> sub forms -> sub forms -> questions
                            "sub_form__questions",
                            queryset=question_queryset.prefetch_related(
                                Prefetch(
                                    # root form -> sub forms -> sub forms -> row forms -> questions
                                    "row_form__questions",
                                    queryset=question_queryset,
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ]


def update_calc_dependents(slug, old_expr, new_expr):
    jexl = QuestionJexl()
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


def update_or_create_calc_answer(
    question, document, struc=None, update_dependents=True
):
    root_doc = document.family

    if not struc:
        struc = structure.FieldSet(root_doc, root_doc.form)

    field = struc.get_field(question.slug)

    # skip if question doesn't exist in this document structure
    if field is None:
        return

    jexl = QuestionJexl(
        {"form": field.form, "document": field.document, "structure": field.parent()}
    )

    # Ignore errors because we evaluate greedily as soon as possible. At
    # this moment we might be missing some answers or the expression might
    # be invalid, in which case we return None
    value = jexl.evaluate(field.question.calc_expression, raise_on_error=False)

    answer, _ = models.Answer.objects.update_or_create(
        question=question, document=field.document, defaults={"value": value}
    )
    # also save new answer to structure for reuse
    struc.set_answer(question.slug, answer)

    if update_dependents:
        for _question in models.Question.objects.filter(
            pk__in=field.question.calc_dependents
        ):
            update_or_create_calc_answer(_question, document, struc)
