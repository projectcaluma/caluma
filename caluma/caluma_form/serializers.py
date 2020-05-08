from django.db import transaction
from rest_framework import exceptions
from rest_framework.serializers import (
    CharField,
    DateField,
    FloatField,
    IntegerField,
    ListField,
    PrimaryKeyRelatedField,
)

from ..caluma_core import serializers
from . import models, validators
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

        for sort, form_question in enumerate(
            reversed(models.FormQuestion.objects.filter(form=source)), start=1
        ):
            models.FormQuestion.objects.create(
                sort=sort,
                form=form,
                question=form_question.question,
                created_by_user=user.username,
                created_by_group=user.group,
            )

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
                self.instance.questions.all().order_by("formquestion__sort"), start=1
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
        for question_option in new_question_options:
            question_option.save()

        return question

    class Meta:
        model = models.Question
        fields = ("slug", "label", "source")


class SaveQuestionSerializer(serializers.ModelSerializer):
    is_hidden = QuestionJexlField(required=False)
    is_required = QuestionJexlField(required=False)

    def validate(self, data):
        validators.QuestionValidator().validate(data)
        return super().validate(data)

    class Meta:
        model = models.Question
        fields = (
            "slug",
            "label",
            "info_text",
            "is_required",
            "is_hidden",
            "meta",
            "is_archived",
        )


class SaveTextQuestionSerializer(SaveQuestionSerializer):
    min_length = IntegerField(min_value=1, required=False, allow_null=True)
    max_length = IntegerField(min_value=1, required=False, allow_null=True)
    format_validators = ListField(child=CharField(), required=False)

    def validate(self, data):
        data["type"] = models.Question.TYPE_TEXT
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + (
            "min_length",
            "max_length",
            "placeholder",
            "format_validators",
        )


class SaveTextareaQuestionSerializer(SaveQuestionSerializer):
    min_length = IntegerField(min_value=1, required=False, allow_null=True)
    max_length = IntegerField(min_value=1, required=False, allow_null=True)
    format_validators = ListField(child=CharField(), required=False)

    def validate(self, data):
        data["type"] = models.Question.TYPE_TEXTAREA
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + (
            "min_length",
            "max_length",
            "placeholder",
            "format_validators",
        )


class SaveDateQuestionSerializer(SaveQuestionSerializer):
    def validate(self, data):
        data["type"] = models.Question.TYPE_DATE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields


class SaveQuestionOptionsMixin(object):
    def create_question_options(self, question, options):
        user = self.context["request"].user
        question_options = [
            models.QuestionOption(
                sort=sort,
                question=question,
                option=option,
                created_by_user=user.username,
                created_by_group=user.group,
            )
            for sort, option in enumerate(reversed(options), start=1)
        ]
        for question_option in question_options:
            question_option.save()

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


class SaveDynamicChoiceQuestionSerializer(SaveQuestionSerializer):
    data_source = CharField()

    def validate(self, data):
        data["type"] = models.Question.TYPE_DYNAMIC_CHOICE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("data_source",)


class SaveDynamicMultipleChoiceQuestionSerializer(SaveQuestionSerializer):
    data_source = CharField()

    def validate(self, data):
        data["type"] = models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ("data_source",)


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
        fields = SaveQuestionSerializer.Meta.fields + (
            "min_value",
            "max_value",
            "placeholder",
        )


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
        fields = SaveQuestionSerializer.Meta.fields + (
            "min_value",
            "max_value",
            "placeholder",
        )


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


class SaveFileQuestionSerializer(SaveQuestionSerializer):
    def validate(self, data):
        data["type"] = models.Question.TYPE_FILE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields


class SaveStaticQuestionSerializer(SaveQuestionSerializer):
    static_content = CharField(required=False)

    def validate(self, data):
        data["type"] = models.Question.TYPE_STATIC
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = (
            "label",
            "slug",
            "info_text",
            "is_hidden",
            "meta",
            "is_archived",
            "static_content",
        )


class SaveOptionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("slug", "label", "is_archived", "meta")
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


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = ("id", "form", "meta")


class SaveAnswerSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if "value" not in data:
            data["value"] = None
        validators.AnswerValidator().validate(**data, user=self.context["request"].user)
        return super().validate(data)

    class Meta:
        model = models.Answer
        fields = ("question", "document", "meta", "value")


class SaveDocumentStringAnswerSerializer(SaveAnswerSerializer):
    value = CharField(trim_whitespace=False, allow_blank=True, required=False)

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentListAnswerSerializer(SaveAnswerSerializer):
    value = ListField(child=CharField(), required=False)

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentIntegerAnswerSerializer(SaveAnswerSerializer):
    value = IntegerField(required=False)

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentFloatAnswerSerializer(SaveAnswerSerializer):
    value = FloatField(required=False)

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentDateAnswerSerializer(SaveAnswerSerializer):
    value = DateField(source="date", required=False)

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentTableAnswerSerializer(SaveAnswerSerializer):
    value = serializers.GlobalIDPrimaryKeyRelatedField(
        source="documents",
        queryset=models.Document.objects,
        many=True,
        required=False,
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
                    f"Document {document.pk} is not of form type {question.row_form.pk}."
                )

        return data

    def create_answer_documents(self, answer, documents):
        family = answer.document.family
        document_ids = [document.pk for document in documents]

        for sort, document_id in enumerate(reversed(document_ids), start=1):
            ans_doc, created = models.AnswerDocument.objects.get_or_create(
                answer=answer, document_id=document_id, defaults={"sort": sort}
            )
            if not created and ans_doc.sort != sort:
                ans_doc.sort = sort
                ans_doc.save()
            if created:
                # Already-existing documents are already in the family,
                # so we're updating only the newly attached rows
                ans_doc.document.set_family(family)

    @transaction.atomic
    def create(self, validated_data):
        documents = validated_data.pop("documents")
        instance = super().create(validated_data)
        self.create_answer_documents(instance, documents)
        return instance

    def unlink_unused_rows(self, docs_to_keep):
        existing = models.AnswerDocument.objects.filter(answer=self.instance).exclude(
            document__in=docs_to_keep
        )
        for ans_doc in list(existing.select_related("document")):
            # Set document to be its own family
            # TODO: Can/should we delete the detached documents?
            ans_doc.document.set_family(ans_doc.document)
            ans_doc.delete()

    @transaction.atomic
    def update(self, instance, validated_data):
        documents = validated_data.pop("documents")

        self.unlink_unused_rows(docs_to_keep=documents)

        instance = super().update(instance, validated_data)
        self.create_answer_documents(instance, documents)
        return instance

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentFileAnswerSerializer(SaveAnswerSerializer):
    value = CharField(write_only=True, source="file", required=False)
    value_id = PrimaryKeyRelatedField(read_only=True, source="file", required=False)

    def set_file(self, validated_data):
        file_name = validated_data.get("file")
        file = models.File.objects.create(name=file_name)
        validated_data["file"] = file
        return validated_data

    def create(self, validated_data):
        validated_data = self.set_file(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.file.name is not validated_data["file"]:
            instance.file.delete()
            validated_data = self.set_file(validated_data)
        return super().update(instance, validated_data)

    class Meta(SaveAnswerSerializer.Meta):
        fields = SaveAnswerSerializer.Meta.fields + ("value_id",)


class RemoveAnswerSerializer(serializers.ModelSerializer):
    answer = PrimaryKeyRelatedField(queryset=models.Answer.objects.all())

    def update(self, instance, validated_data):
        instance.delete()
        return instance

    class Meta:
        fields = ("answer",)
        model = models.Answer


class RemoveDocumentSerializer(serializers.ModelSerializer):
    document = serializers.GlobalIDField(source="id")

    def update(self, instance, validated_data):
        if hasattr(instance, "case"):
            raise Exception("You cannot remove a Document, if it's attached to a case.")

        for answer in instance.answers.filter(
            question__type=models.Question.TYPE_TABLE
        ):
            answer.documents.all().delete()

        instance.delete()

        return instance

    class Meta:
        fields = ("document",)
        model = models.Document


class CopyDocumentSerializer(serializers.ModelSerializer):
    source = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Document.objects, required=True
    )

    @transaction.atomic
    def create(self, validated_data):
        return validated_data["source"].copy()

    class Meta:
        model = models.Document
        fields = ("source",)
