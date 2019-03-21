from django.db import transaction
from django.db.models import Q
from rest_framework import exceptions
from rest_framework.serializers import (
    CharField,
    DateField,
    FloatField,
    IntegerField,
    ListField,
)

from . import models, validators
from ..core import serializers
from .jexl import QuestionJexl


class QuestionJexlField(serializers.JexlField):
    def __init__(self, **kwargs):
        super().__init__(QuestionJexl(), **kwargs)


class SaveFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ("slug", "name", "description", "meta", "is_archived", "is_published")


class CopyFormSerializer(serializers.ModelSerializer):
    source = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Form.objects, required=True
    )

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        source = validated_data["source"]
        validated_data["meta"] = dict(source.meta)

        form = super().create(validated_data)

        new_form_questions = [
            models.FormQuestion(
                sort=sort,
                form=form,
                question=form_question.question,
                created_by_user=user.username,
                created_by_group=user.group,
            )
            for sort, form_question in enumerate(
                reversed(models.FormQuestion.objects.filter(form=source)), start=1
            )
        ]
        models.FormQuestion.objects.bulk_create(new_form_questions)

        return form

    class Meta:
        model = models.Form
        fields = ("slug", "name", "description", "source", "is_published")


class AddFormQuestionSerializer(serializers.ModelSerializer):
    form = serializers.GlobalIDField(source="slug")
    question = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Question.objects
    )

    def update(self, instance, validated_data):
        # default sort is 0, as per default form question are sorted
        # in descending order this will be at the end
        _, created = models.FormQuestion.objects.get_or_create(
            form=self.instance, question=validated_data["question"]
        )

        if created:
            # reassign sort from start 1 so a newly added item with sort 0 will
            # be at the end again
            for sort, question in enumerate(
                reversed(self.instance.questions.all()), start=1
            ):
                models.FormQuestion.objects.filter(
                    form=instance, question=question
                ).update(sort=sort)

        return instance

    class Meta:
        fields = ("form", "question")
        model = models.Form


class RemoveFormQuestionSerializer(serializers.ModelSerializer):
    form = serializers.GlobalIDField(source="slug")
    question = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Question.objects
    )

    def update(self, instance, validated_data):
        models.FormQuestion.objects.filter(
            form=instance, question=validated_data["question"]
        ).delete()
        return instance

    class Meta:
        fields = ("form", "question")
        model = models.Form


class FormQuestionRelatedField(serializers.GlobalIDPrimaryKeyRelatedField):
    def get_queryset(self):
        form = self.parent.parent.instance
        return form.questions.all()


class ReorderFormQuestionsSerializer(serializers.ModelSerializer):
    form = serializers.GlobalIDField(source="slug")
    questions = FormQuestionRelatedField(many=True)

    def update(self, instance, validated_data):
        questions = validated_data["questions"]
        curr_questions = set(instance.questions.all())

        if len(questions) != len(curr_questions) or set(questions) - set(
            instance.questions.all()
        ):
            raise exceptions.ValidationError(
                "Input questions are not the same as current form questions"
            )

        for sort, question in enumerate(reversed(questions), start=1):
            models.FormQuestion.objects.filter(form=instance, question=question).update(
                sort=sort
            )

        return instance

    class Meta:
        fields = ("form", "questions")
        model = models.Form


class CopyQuestionSerializer(serializers.ModelSerializer):
    source = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Question.objects, required=True
    )

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        source = validated_data["source"]
        validated_data["type"] = source.type
        validated_data["is_required"] = source.is_required
        validated_data["is_hidden"] = source.is_hidden
        validated_data["configuration"] = dict(source.configuration)
        validated_data["meta"] = dict(source.meta)
        validated_data["row_form"] = source.row_form

        question = super().create(validated_data)

        new_question_options = [
            models.QuestionOption(
                sort=sort,
                question=question,
                option=question_option.option,
                created_by_user=user.username,
                created_by_group=user.group,
            )
            for sort, question_option in enumerate(
                reversed(models.QuestionOption.objects.filter(question=source)), start=1
            )
        ]
        models.QuestionOption.objects.bulk_create(new_question_options)

        return question

    class Meta:
        model = models.Question
        fields = ("slug", "label", "source")


class SaveQuestionSerializer(serializers.ModelSerializer):
    is_hidden = QuestionJexlField(required=False)
    is_required = QuestionJexlField(required=False)

    class Meta:
        model = models.Question
        fields = ("slug", "label", "is_required", "is_hidden", "meta", "is_archived")


class SaveTextQuestionSerializer(SaveQuestionSerializer):
    max_length = IntegerField(min_value=1, required=False, allow_null=True)

    def validate(self, data):
        data["type"] = models.Question.TYPE_TEXT
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("max_length",)


class SaveTextareaQuestionSerializer(SaveQuestionSerializer):
    max_length = IntegerField(min_value=1, required=False, allow_null=True)

    def validate(self, data):
        data["type"] = models.Question.TYPE_TEXTAREA
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("max_length",)


class SaveDateQuestionSerializer(SaveQuestionSerializer):
    def validate(self, data):
        data["type"] = models.Question.TYPE_DATE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields


class SaveQuestionOptionsMixin(object):
    def create_question_options(self, question, options):
        user = self.context["request"].user
        question_option = [
            models.QuestionOption(
                sort=sort,
                question=question,
                option=option,
                created_by_user=user.username,
                created_by_group=user.group,
            )
            for sort, option in enumerate(reversed(options), start=1)
        ]
        models.QuestionOption.objects.bulk_create(question_option)

    @transaction.atomic
    def create(self, validated_data):
        options = validated_data.pop("options")
        instance = super().create(validated_data)
        self.create_question_options(instance, options)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        options = validated_data.pop("options")
        models.QuestionOption.objects.filter(question=instance).delete()
        instance = super().update(instance, validated_data)
        self.create_question_options(instance, options)
        return instance


class SaveMultipleChoiceQuestionSerializer(
    SaveQuestionOptionsMixin, SaveQuestionSerializer
):
    options = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Option.objects.all(), many=True, required=True
    )

    def validate(self, data):
        data["type"] = models.Question.TYPE_MULTIPLE_CHOICE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("options",)


class SaveChoiceQuestionSerializer(SaveQuestionOptionsMixin, SaveQuestionSerializer):
    options = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Option.objects.all(), many=True, required=True
    )

    def validate(self, data):
        data["type"] = models.Question.TYPE_CHOICE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("options",)


class SaveFloatQuestionSerializer(SaveQuestionSerializer):
    min_value = FloatField(required=False, allow_null=True)
    max_value = FloatField(required=False, allow_null=True)

    def validate(self, data):
        min_value = (
            data.get("min_value")
            if data.get("min_value") is not None
            else float("-inf")
        )
        max_value = (
            data.get("max_value") if data.get("max_value") is not None else float("inf")
        )

        if min_value > max_value:
            raise exceptions.ValidationError(
                f"max_value {max_value} is smaller than {min_value}"
            )

        data["type"] = models.Question.TYPE_FLOAT
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("min_value", "max_value")


class SaveIntegerQuestionSerializer(SaveQuestionSerializer):
    min_value = IntegerField(required=False, allow_null=True)
    max_value = IntegerField(required=False, allow_null=True)

    def validate(self, data):
        min_value = (
            data.get("min_value")
            if data.get("min_value") is not None
            else float("-inf")
        )
        max_value = (
            data.get("max_value") if data.get("max_value") is not None else float("inf")
        )

        if min_value > max_value:
            raise exceptions.ValidationError(
                f"max_value {max_value} is smaller than {min_value}"
            )

        data["type"] = models.Question.TYPE_INTEGER
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("min_value", "max_value")


class SaveTableQuestionSerializer(SaveQuestionSerializer):
    row_form = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Form.objects,
        required=True,
        help_text=models.Question._meta.get_field("row_form").help_text,
    )

    def validate(self, data):
        data["type"] = models.Question.TYPE_TABLE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("row_form",)


class SaveFormQuestionSerializer(SaveQuestionSerializer):
    sub_form = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Form.objects, required=True
    )

    def validate(self, data):
        data["type"] = models.Question.TYPE_FORM
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("sub_form",)


class SaveOptionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("slug", "label", "meta")
        model = models.Option


class CopyOptionSerializer(serializers.ModelSerializer):
    source = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Option.objects, required=True
    )

    def create(self, validated_data):
        source = validated_data["source"]
        validated_data["meta"] = dict(source.meta)
        return super().create(validated_data)

    class Meta:
        fields = ("slug", "label", "source")
        model = models.Option


class RemoveOptionSerializer(serializers.ModelSerializer):
    option = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        models.Option.objects.filter(pk=instance).delete()
        return instance

    class Meta:
        fields = ("option",)
        model = models.Option


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = ("form", "meta")


class SaveAnswerSerializer(serializers.ModelSerializer):
    def validate(self, data):
        validators.AnswerValidator().validate(**data)
        return super().validate(data)

    class Meta:
        model = models.Answer
        fields = ("question", "document", "meta", "value")


class SaveDocumentStringAnswerSerializer(SaveAnswerSerializer):
    value = CharField()

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentListAnswerSerializer(SaveAnswerSerializer):
    value = ListField(child=CharField())

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentIntegerAnswerSerializer(SaveAnswerSerializer):
    value = IntegerField()

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentFloatAnswerSerializer(SaveAnswerSerializer):
    value = FloatField()

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentDateAnswerSerializer(SaveAnswerSerializer):
    value = DateField()

    class Meta(SaveAnswerSerializer.Meta):
        pass


def _get_document_tree(document_id):
    answers = models.AnswerDocument.objects.filter(document_id=document_id).values(
        "answer"
    )
    child_documents = models.Document.objects.filter(
        Q(answers=answers) | Q(parent_answers=answers)
    ).distinct()

    for child_document in child_documents:
        yield from _get_document_tree(child_document.pk)

    yield document_id


class SaveDocumentTableAnswerSerializer(SaveAnswerSerializer):
    value = serializers.GlobalIDPrimaryKeyRelatedField(
        source="documents",
        queryset=models.Document.objects,
        many=True,
        required=True,
        help_text="List of document IDs representing the rows in the table.",
    )

    def validate(self, data):
        documents = (
            data.get("documents")
            or self.instance
            and self.instance.documents.all()
            or []
        )
        question = data.get("question") or self.instance and self.instance.question

        for document in documents:
            if document.form_id != question.row_form_id:
                raise exceptions.ValidationError(
                    f"Document {document.pk} is not of form type {question.form.pk}."
                )

        return super().validate(data)

    def create_answer_documents(self, answer, documents):
        family = answer.document.family
        document_ids = [document.pk for document in documents]

        for sort, document_id in enumerate(reversed(document_ids), start=1):
            models.AnswerDocument.objects.create(
                answer=answer, document_id=document_id, sort=sort
            )

        # attach document answers to root document family
        models.Document.objects.filter(
            family__in=models.Document.objects.filter(pk__in=document_ids).values(
                "family"
            )
        ).update(family=family)

    @transaction.atomic
    def create(self, validated_data):
        documents = validated_data.pop("documents")
        instance = super().create(validated_data)
        self.create_answer_documents(instance, documents)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        documents = validated_data.pop("documents")

        # detach answers to its own family tree
        answer_documents = models.AnswerDocument.objects.filter(answer=instance)
        for answer_document in models.Document.objects.filter(
            pk__in=answer_documents.values("document")
        ):
            children = _get_document_tree(answer_document.pk)
            models.Document.objects.filter(pk__in=children).update(
                family=answer_document.pk
            )
        answer_documents.delete()

        instance = super().update(instance, validated_data)
        self.create_answer_documents(instance, documents)
        return instance

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentFormAnswerSerializer(SaveAnswerSerializer):
    value = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Document.objects,
        required=True,
        help_text="Document IDs representing the content of the form.",
        source="value_document",
    )

    def validate(self, data):
        document = (
            data.get("value_document") or self.instance and self.instance.value_document
        )
        question = data.get("question") or self.instance and self.instance.question

        if document.form_id != question.row_form_id:
            raise exceptions.ValidationError(
                f"Document {document.pk} is of form type {document.form_id}, but should be of type {question.row_form.pk}."
            )

        return super().validate(data)

    def set_family(self, answer, document):
        family = answer.document.family

        # attach document answers to root document family
        models.Document.objects.filter(
            family=models.Document.objects.get(pk=document.id).family
        ).update(family=family)

    @transaction.atomic
    def create(self, validated_data):
        document = validated_data.get("document")
        instance = super().create(validated_data)
        self.set_family(instance, document)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        value_document = validated_data.get("value_document")

        # detach current answer document to its own family tree
        answer_document = instance.value_document
        if answer_document:
            children = _get_document_tree(answer_document.pk)
            models.Document.objects.filter(pk__in=children).update(
                family=answer_document.pk
            )

        instance = super().update(instance, validated_data)
        self.set_family(instance, value_document)
        return instance

    class Meta(SaveAnswerSerializer.Meta):
        pass
