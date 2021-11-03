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
    def create(model: BaseModel, validated_data, user: Optional[BaseUser] = None):
        if user:
            validated_data["created_by_user"] = user.username if user else None
            validated_data["created_by_group"] = user.group if user else None
            validated_data["modified_by_user"] = user.username if user else None
            validated_data["modified_by_group"] = user.group if user else None

        return model.objects.create(**validated_data)

    @staticmethod
    @transaction.atomic
    def update(instance: BaseModel, validated_data, user: Optional[BaseUser] = None):
        if user:
            validated_data["modified_by_user"] = user.username
            validated_data["modified_by_group"] = user.group

        update_model(instance, validated_data)
        instance.refresh_from_db()

        return instance


class SaveAnswerLogic:
    @classmethod
    def get_new_answer(cls, data, user, answer):
        validated_data = cls.pre_save(
            cls.validate_for_save(data, user, answer=answer, origin=True)
        )

        if answer is None:
            answer = cls.create(validated_data, user)
        else:
            answer = cls.update(answer, validated_data, user)

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

        answer = BaseLogic.create(models.Answer, validated_data, user)

        if answer.question.type == models.Question.TYPE_TABLE:
            answer.create_answer_documents(documents)

        return answer

    @staticmethod
    @transaction.atomic
    def update(answer, validated_data, user: Optional[BaseUser] = None):
        if answer.question.type == models.Question.TYPE_TABLE:
            documents = validated_data.pop("documents")
            answer.unlink_unused_rows(docs_to_keep=documents)

        if (
            answer.question.type == models.Question.TYPE_FILE
            and answer.file.name is not validated_data["file"]
        ):
            answer.file.delete()
            validated_data = __class__.set_file(validated_data)

        BaseLogic.update(answer, validated_data, user)

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
            models.Question.TYPE_CALCULATED_FLOAT,
            models.Question.TYPE_ACTION_BUTTON,
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
    def update(
        answer, validated_data, user: Optional[BaseUser] = None
    ) -> models.Answer:
        return SaveAnswerLogic.update(answer, validated_data, user)


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
        document = BaseLogic.create(models.Document, validated_data, user=user)

        document = SaveDocumentLogic._set_default_answers_for_form(
            document.form, document, user
        )
        return document

    @staticmethod
    @transaction.atomic
    def update(document, validated_data, user: Optional[BaseUser] = None):
        BaseLogic.update(document, validated_data, user)


class CopyFormLogic:
    @staticmethod
    def copy(validated_data: dict, user: Optional[BaseUser] = None):
        source = validated_data["source"]
        validated_data["meta"] = dict(source.meta)
        form = BaseLogic.create(models.Form, validated_data, user=user)

        for form_question in models.FormQuestion.objects.filter(form=source):
            BaseLogic.create(
                models.FormQuestion,
                {
                    "form": form,
                    "sort": form_question.sort,
                    "question": form_question.question,
                },
                user,
            )

        return form
