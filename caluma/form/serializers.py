from django.db import transaction
from rest_framework import exceptions
from rest_framework.serializers import FloatField, IntegerField

from . import models
from .. import serializers
from .jexl import QuestionJexl


class QuestionJexlField(serializers.JexlField):
    def __init__(self, **kwargs):
        super().__init__(QuestionJexl(), **kwargs)


class SaveFormSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FormSpecification
        fields = ("slug", "name", "description", "meta")


class ArchiveFormSpecificationSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        instance.is_archived = True
        instance.save(update_fields=["is_archived"])
        return instance

    class Meta:
        fields = ("id",)
        model = models.FormSpecification


class AddFormSpecificationQuestionSerializer(serializers.ModelSerializer):
    form_specification = serializers.GlobalIDField(source="slug")
    question = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Question.objects
    )

    def update(self, instance, validated_data):
        models.FormSpecificationQuestion.objects.get_or_create(
            form_specification=self.instance, question=validated_data["question"]
        )
        return instance

    class Meta:
        fields = ("form_specification", "question")
        model = models.FormSpecification


class RemoveFormSpecificationQuestionSerializer(serializers.ModelSerializer):
    form_specification = serializers.GlobalIDField(source="slug")
    question = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Question.objects
    )

    def update(self, instance, validated_data):
        models.FormSpecificationQuestion.objects.filter(
            form_specification=instance, question=validated_data["question"]
        ).delete()
        return instance

    class Meta:
        fields = ("form_specification", "question")
        model = models.FormSpecification


class FormSpecificationQuestionRelatedField(serializers.GlobalIDPrimaryKeyRelatedField):
    def get_queryset(self):
        form_specification = self.parent.parent.instance
        return form_specification.questions.all()


class ReorderFormSpecificationQuestionsSerializer(serializers.ModelSerializer):
    form_specification = serializers.GlobalIDField(source="slug")
    questions = FormSpecificationQuestionRelatedField(many=True)

    def update(self, instance, validated_data):
        questions = validated_data["questions"]
        for sort, question in enumerate(reversed(questions)):
            models.FormSpecificationQuestion.objects.filter(
                form_specification=instance, question=question
            ).update(sort=sort)

        return instance

    class Meta:
        fields = ("form_specification", "questions")
        model = models.FormSpecification


class PublishFormSpecificationSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        instance.is_published = True
        instance.save(update_fields=["is_published"])
        return instance

    class Meta:
        fields = ("id",)
        model = models.FormSpecification


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
        question_option = [
            models.QuestionOption(sort=sort, question=question, option=option)
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


class SaveOptionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("slug", "label", "meta")
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
