from typing import Optional

from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from caluma.caluma_core.models import BaseModel
from caluma.caluma_form import models, validators
from caluma.caluma_user.models import BaseUser
from caluma.utils import update_model


class BaseLogic:
    @staticmethod
    @transaction.atomic
    def create(model: BaseModel, user: Optional[BaseUser] = None, **kwargs):
        if user:
            kwargs["created_by_user"] = user
            kwargs["created_by_group"] = user.group

        return model.objects.create(**kwargs)


class SaveAnswerLogic:
    @classmethod
    def get_new_answer(cls, data, user, answer):
        validated_data = cls.pre_save(
            cls.validate_for_save(data, user, answer=answer, origin=True)
        )

        if answer is None:
            answer = cls.create(validated_data, user)
        else:
            answer = cls.update(validated_data, answer)

        return cls.post_save(answer)

    @staticmethod
    def validate_for_save(
        data: dict, user: BaseUser, answer: models.Answer = None, origin: bool = False
    ) -> dict:
        question = data["question"]

        # Save empty answer by omitting the value property since graphql-core
        # doesn't allow `null` literals yet
        if "value" not in data:
            data["value"] = None

        # make data from python api similar to graphql api
        if question.type == models.Question.TYPE_TABLE and not data.get("documents"):
            data["documents"] = (
                models.Document.objects.filter(pk__in=data["value"])
                if data["value"]
                else models.Document.objects.none()
            )
            del data["value"]
        elif question.type == models.Question.TYPE_FILE and not data.get("file"):
            data["file"] = data["value"]
            del data["value"]
        elif question.type == models.Question.TYPE_DATE and not data.get("date"):
            data["date"] = data["value"]
            del data["value"]

        validators.AnswerValidator().validate(
            **data, user=user, instance=answer, origin=origin
        )

        return data

    @staticmethod
    def pre_save(validated_data: dict) -> dict:
        # TODO emit events
        return validated_data

    @staticmethod
    def post_save(answer: models.Answer) -> models.Answer:
        # TODO emit events
        return answer

    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user: Optional[BaseUser] = None) -> models.Answer:
        if validated_data["question"].type == models.Question.TYPE_FILE:
            validated_data = __class__.set_file(validated_data)

        if validated_data["question"].type == models.Question.TYPE_TABLE:
            documents = validated_data.pop("documents")

        answer = BaseLogic.create(models.Answer, user, **validated_data)

        if answer.question.type == models.Question.TYPE_TABLE:
            answer.create_answer_documents(documents)

        return answer

    @staticmethod
    @transaction.atomic
    def update(validated_data, answer):
        if answer.question.type == models.Question.TYPE_TABLE:
            documents = validated_data.pop("documents")
            answer.unlink_unused_rows(docs_to_keep=documents)

        if (
            answer.question.type == models.Question.TYPE_FILE
            and answer.file.name is not validated_data["file"]
        ):
            answer.file.delete()
            validated_data = __class__.set_file(validated_data)

        update_model(answer, validated_data)

        if answer.question.type == models.Question.TYPE_TABLE:
            answer.create_answer_documents(documents)

        answer.refresh_from_db()
        return answer

    @staticmethod
    def set_file(validated_data):
        file_name = validated_data.get("file")
        file = models.File.objects.create(name=file_name)
        validated_data["file"] = file
        return validated_data


class SaveDefaultAnswerLogic(SaveAnswerLogic):
    @staticmethod
    def validate_for_save(
        data: dict, user: BaseUser, answer: models.Answer = None, origin: bool = False
    ) -> dict:
        if data["question"].type in [
            models.Question.TYPE_FILE,
            models.Question.TYPE_STATIC,
            models.Question.TYPE_DYNAMIC_CHOICE,
            models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
        ]:
            raise ValidationError(
                f'Can\'t save default_answer for question of type "{data["question"].type}"'
            )

        data["document"] = None  # send None as document for validation
        return SaveAnswerLogic.validate_for_save(data, user, answer, origin)

    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user: Optional[BaseUser] = None) -> models.Answer:
        answer = SaveAnswerLogic.create(validated_data, user)
        answer.question.default_answer = answer
        answer.question.save()

        return answer

    @staticmethod
    @transaction.atomic
    def update(validated_data, answer):
        return SaveAnswerLogic.update(validated_data, answer)


class SaveDocumentLogic:
    @staticmethod
    def _set_default_answers_for_form(form, document, user):
        """
        Set answers for questions with a default_answer.

        This method sets the default_answers on a new document. It recusively travels
        through the form and it's subforms, looking for questions that have a
        default_answer.
        For adding the answers, it does one query per form and one query per
        row_document.
        """
        answers = []
        for question in form.questions.filter(
            Q(default_answer__isnull=False) | Q(type=models.Question.TYPE_FORM)
        ).iterator():
            if question.type == models.Question.TYPE_FORM:
                if question.sub_form is not None:
                    document = SaveDocumentLogic._set_default_answers_for_form(
                        question.sub_form, document, user
                    )
                continue
            answers.append(
                question.default_answer.copy(document_family=document.family, user=user)
            )
        document.answers.add(*answers)
        return document

    @staticmethod
    @transaction.atomic
    def create(
        validated_data: dict, user: Optional[BaseUser] = None
    ) -> models.Document:
        document = BaseLogic.create(model=models.Document, user=user, **validated_data)

        document = SaveDocumentLogic._set_default_answers_for_form(
            document.form, document, user
        )
        return document

    @staticmethod
    @transaction.atomic
    def update(document, **kwargs):
        update_model(document, kwargs)
