from django.db.models import Q

from caluma.caluma_form import models


def forms_containing_question(question: models.Question) -> list[models.Form]:
    """
    Return list of all forms that have the given quesiton in their structure.

    This contains indirect structures as well, so you can use it to find all
    documents where the given question is part of the data.
    """
    result = []
    for fq in models.FormQuestion.objects.filter(question=question).select_related(
        "form"
    ):
        form = fq.form
        result.append(form)
        parents = models.Question.objects.filter(Q(row_form=form) | Q(sub_form=form))
        for parent in parents:
            result.extend(forms_containing_question(parent))

    return result
