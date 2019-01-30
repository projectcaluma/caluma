from django.db import transaction
from rest_framework import exceptions
from rest_framework.serializers import CharField, FloatField, IntegerField, ListField

from . import models, validators
from ..core import serializers
from .jexl import QuestionJexl


class QuestionJexlField(serializers.JexlField):
    def __init__(self, **kwargs):
        super().__init__(QuestionJexl(), **kwargs)


class SaveFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ("slug", "name", "description", "meta")


class ArchiveFormSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        instance.is_archived = True
        instance.save(update_fields=["is_archived"])
        return instance

    class Meta:
        fields = ("id",)
        model = models.Form


class AddFormQuestionSerializer(serializers.ModelSerializer):
    form = serializers.GlobalIDField(source="slug")
    question = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Question.objects
    )

    def update(self, instance, validated_data):
        models.FormQuestion.objects.get_or_create(
            form=self.instance, question=validated_data["question"]
        )
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

        for sort, question in enumerate(reversed(questions)):
            models.FormQuestion.objects.filter(form=instance, question=question).update(
                sort=sort
            )

        return instance

    class Meta:
        fields = ("form", "questions")
        model = models.Form


class PublishFormSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        instance.is_published = True
        instance.save(update_fields=["is_published"])
        return instance

    class Meta:
        fields = ("id",)
        model = models.Form


class SaveQuestionSerializer(serializers.ModelSerializer):
    is_hidden = QuestionJexlField(required=False)
    is_required = QuestionJexlField(required=False)

    class Meta:
        model = models.Question
        fields = ("slug", "label", "is_required", "is_hidden", "meta")


class SaveTextQuestionSerializer(SaveQuestionSerializer):
    max_length = IntegerField(min_value=1, required=False, allow_null=True)

    def validate(self, data):
        data["type"] = models.Question.TYPE_TEXT
        return data

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("max_length",)


class SaveTextareaQuestionSerializer(SaveQuestionSerializer):
    max_length = IntegerField(min_value=1, required=False, allow_null=True)

    def validate(self, data):
        data["type"] = models.Question.TYPE_TEXTAREA
        return data

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("max_length",)


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
            for sort, option in enumerate(reversed(options))
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


class SaveCheckboxQuestionSerializer(SaveQuestionOptionsMixin, SaveQuestionSerializer):
    options = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Option.objects.all(), many=True, required=True
    )

    def validate(self, data):
        data["type"] = models.Question.TYPE_CHECKBOX
        return data

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("options",)


class SaveRadioQuestionSerializer(SaveQuestionOptionsMixin, SaveQuestionSerializer):
    options = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Option.objects.all(), many=True, required=True
    )

    def validate(self, data):
        data["type"] = models.Question.TYPE_RADIO
        return data

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
        return data

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
        return data

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("min_value", "max_value")


class SaveTableQuestionSerializer(SaveQuestionSerializer):
    row_form = serializers.GlobalIDPrimaryKeyRelatedField(
        required=True, help_text=models.Question._meta.get_field("row_form").help_text
    )

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("row_form",)


class SaveOptionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("slug", "label", "meta")
        model = models.Option


class RemoveOptionSerializer(serializers.ModelSerializer):
    option = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        models.Option.objects.filter(pk=instance).delete()
        return instance

    class Meta:
        fields = ("option",)
        model = models.Option


class ArchiveQuestionSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        instance.is_archived = True
        instance.save(update_fields=["is_archived"])
        return instance

    class Meta:
        fields = ("id",)
        model = models.Question


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = ("form", "meta")


class SaveAnswerSerializer(serializers.ModelSerializer):
    def validate(self, data):
        validators.AnswerValidator().validate(**data)
        return data

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
            data.get("documents") or self.instance and self.instance.documents or []
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

        for sort, document_id in enumerate(reversed(document_ids)):
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

    def _get_document_tree(self, document_id):
        answers = models.AnswerDocument.objects.filter(document_id=document_id).values(
            "answer"
        )
        child_documents = models.Document.objects.filter(answers=answers).distinct()

        for child_document in child_documents:
            yield from self._get_document_tree(child_document.pk)

        yield document_id

    @transaction.atomic
    def update(self, instance, validated_data):
        documents = validated_data.pop("documents")

        # detach answers to its own family tree
        answer_documents = models.AnswerDocument.objects.filter(answer=instance)
        for answer_document in models.Document.objects.filter(
            pk__in=answer_documents.values("document")
        ):
            children = self._get_document_tree(answer_document.pk)
            models.Document.objects.filter(pk__in=children).update(
                family=answer_document.pk
            )
        answer_documents.delete()

        instance = super().update(instance, validated_data)
        self.create_answer_documents(instance, documents)
        return instance

    class Meta(SaveAnswerSerializer.Meta):
        pass
