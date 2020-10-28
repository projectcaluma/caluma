from typing import Any, Optional

from caluma.caluma_form import domain_logic, models
from caluma.caluma_user.models import BaseUser


def save_answer(
    question: models.Question,
    document: models.Document,
    user: Optional[BaseUser] = None,
    value: Optional[Any] = None,
    context: Optional[dict] = None,
    **kwargs
) -> models.Answer:
    """
    Save an answer for given question, document.

    Similar to saveDocumentStringAnswer and the likes, it performes upsert.
    :param value: Must match the question type
    """

    data = {"question": question, "document": document, "value": value}
    data.update(kwargs)

    answer = models.Answer.objects.filter(question=question, document=document).first()

    validated_data = domain_logic.SaveAnswerLogic.pre_save(
        domain_logic.SaveAnswerLogic.validate_for_save(
            data, user, answer=answer, origin=True
        )
    )

    if answer is None:
        answer = domain_logic.SaveAnswerLogic.create(validated_data, user)
    else:
        answer = domain_logic.SaveAnswerLogic.update(validated_data, answer)

    domain_logic.SaveAnswerLogic.post_save(answer)

    return answer
