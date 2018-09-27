from pyjexl.jexl import JEXL
from rest_framework import exceptions
from rest_framework.serializers import FloatField, IntegerField

from . import models
from .. import serializers


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
    def _validate_jexl_expression(self, expression):
        jexl = JEXL()
        # TODO: define transforms e.g. answer
        errors = list(jexl.validate(expression))
        if errors:
            raise exceptions.ValidationError(errors)

        return expression

    def validate_is_required(self, value):
        return self._validate_jexl_expression(value)

    def validate_is_hidden(self, value):
        return self._validate_jexl_expression(value)

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


class SaveCheckboxQuestionSerializer(SaveQuestionSerializer):
    def validate(self, data):
        data["type"] = models.Question.TYPE_CHECKBOX
        return data

    class Meta(SaveQuestionSerializer.Meta):
        pass


class SaveRadioQuestionSerializer(SaveQuestionSerializer):
    def validate(self, data):
        data["type"] = models.Question.TYPE_RADIO
        return data

    class Meta(SaveQuestionSerializer.Meta):
        pass


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


class OptionSerializer(serializers.ModelSerializer):
    def validate(self, data):

        question = data["question"]

        if question.type not in (
            models.Question.TYPE_CHECKBOX,
            models.Question.TYPE_RADIO,
        ):
            raise exceptions.ValidationError(
                "Option may only added to question of type checkbox and radio"
            )

        return data

    class Meta:
        fields = ("slug", "label", "meta", "question")
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
