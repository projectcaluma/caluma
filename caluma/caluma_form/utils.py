from caluma.caluma_form import models, structure
from caluma.caluma_form.jexl import QuestionJexl
from itertools import chain

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


def update_or_create_calc_answer(question, document):
    print("update_or_create", question, document.family.form, document.form, flush=True)
    root_doc = document.family

    struc = structure.FieldSet(root_doc, root_doc.form)
    # TODO: Doesn't get_field return the first field instance it finds in the document for that question, starting from the root document? 
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

    models.Answer.objects.update_or_create(
        question=question, document=field.document, defaults={"value": value}
    )

def update_or_create_calc_answers(questions, document):
    print("bulk update_or_create", questions, document.family.form, document.form, flush=True)
    root_doc = document.family

    struc = structure.FieldSet(root_doc, root_doc.form)
    
    for question in questions:
        field = struc.get_field(question.slug)

        # skip if question doesn't exist in this document structure
        if field is None:
            continue

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

def recalculate_answers_from_document(instance):

    # Only re-evaluate calc-dependents
    if (instance.family or instance).meta.get("_defer_calculation"):
        return

    #print("instance", set(chain(*instance.form.questions.values_list("calc_dependents", flat=True))), flush=True)
    calc_dependent_questions = set(chain(*instance.form.questions.values_list("calc_dependents", flat=True)))

    
    questions = models.Form.get_all_questions(
        [(instance.family or instance).form_id]
    ).filter(type=models.Question.TYPE_CALCULATED_FLOAT)
        
    update_or_create_calc_answers(questions, instance)

    return
    #print("recalc update", calc_dependent_questions, flush=True)
    questions = models.Question.objects.filter(slug__in=calc_dependent_questions)
    update_or_create_calc_answers(questions, instance)
