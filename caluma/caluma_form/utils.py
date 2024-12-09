from caluma.caluma_form import models, structure
from django.db.models import Prefetch
from caluma.caluma_form.jexl import QuestionJexl
from time import time


def build_document_prefetch_statements(prefix="", prefetch_options=False):
    """Build needed prefetch statements to performantly fetch a document.

    This is needed to reduce the query count when almost all the form data
    is needed for a given document, e.g. when recalculating calculated
    answers.
    """

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

    if prefix:
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


def update_or_create_calc_answer(question, document, struc):
    root_doc = document.family

    if not struc:
        print("init structure")
        struc = structure.FieldSet(root_doc, root_doc.form)
    else:
        print("reusing struc")
    start = time()
    field = struc.get_field(question.slug)
    # print(f"get_field: ", time() - start)

    # skip if question doesn't exist in this document structure
    if field is None:
        print("-- didn't find question, stopping")
        return

    jexl = QuestionJexl(
        {"form": field.form, "document": field.document, "structure": field.parent()}
    )

    # Ignore errors because we evaluate greedily as soon as possible. At
    # this moment we might be missing some answers or the expression might
    # be invalid, in which case we return None
    value = jexl.evaluate(field.question.calc_expression, raise_on_error=False)

    models.Answer.objects.update_or_create(
        question=question, document=field.document, defaults={"value": value}
    )

    for _question in models.Question.objects.filter(
        pk__in=field.question.calc_dependents
    ):
        print(f"{question.pk} -> {_question.pk}")
        update_or_create_calc_answer(_question, document, struc)



def recalculate_answers_from_document(instance):
    """When a table row is added, update dependent questions"""
    if (instance.family or instance).meta.get("_defer_calculation"):
        print("- defered")
        return
    print(f"saved document {instance.pk}, recalculate answers")
    for question in models.Form.get_all_questions(
        [(instance.family or instance).form_id]
    ).filter(type=models.Question.TYPE_CALCULATED_FLOAT):
        update_or_create_calc_answer(question, instance)


