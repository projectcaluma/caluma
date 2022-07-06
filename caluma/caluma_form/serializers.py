from django.db import transaction
from rest_framework import exceptions
from rest_framework.serializers import (
    BooleanField,
    CharField,
    DateField,
    FloatField,
    IntegerField,
    ListField,
    PrimaryKeyRelatedField,
)

from ..caluma_core import serializers
from . import domain_logic, models, validators
from .jexl import QuestionJexl


class QuestionJexlField(serializers.JexlField):
    def __init__(self, **kwargs):
        super().__init__(QuestionJexl(), **kwargs)


class ButtonActionField(serializers.CalumaChoiceField):
    def __init__(self, **kwargs):
        super().__init__(models.Question.ACTION_CHOICES, **kwargs)


class ButtonColorField(serializers.CalumaChoiceField):
    def __init__(self, **kwargs):
        super().__init__(models.Question.COLOR_CHOICES, **kwargs)


class SaveFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ["slug", "name", "description", "meta", "is_archived", "is_published"]


class CopyFormSerializer(serializers.ModelSerializer):
    source = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Form.objects, required=True
    )

    @transaction.atomic
    def create(self, validated_data):
        return domain_logic.CopyFormLogic.copy(
            validated_data, user=self.context["request"].user
        )

    class Meta:
        model = models.Form
        fields = ["slug", "name", "description", "source", "is_published"]


class AddFormQuestionSerializer(serializers.ModelSerializer):
    form = serializers.GlobalIDField(source="slug")
    question = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Question.objects
    )

    def update(self, instance, validated_data):
        # default sort is 0, as per default form question are sorted
        # in descending order this will be at the end
        _, created = models.FormQuestion.objects.get_or_create(
            form=self.instance,
            question=validated_data["question"],
            defaults={
                "created_by_user": self.context["request"].user.username,
                "created_by_group": self.context["request"].user.group,
            },
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
        fields = ["form", "question"]
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
        fields = ["form", "question"]
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
        fields = ["form", "questions"]
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
                modified_by_user=user.username,
                modified_by_group=user.group,
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
        fields = ["slug", "label", "source"]


class SaveQuestionSerializer(serializers.ModelSerializer):
    is_hidden = QuestionJexlField(required=False)
    is_required = QuestionJexlField(required=False)

    def validate(self, data):
        validators.QuestionValidator().validate(data)
        return super().validate(data)

    class Meta:
        model = models.Question
        fields = [
            "slug",
            "label",
            "info_text",
            "is_required",
            "is_hidden",
            "meta",
            "is_archived",
        ]


class SaveTextQuestionSerializer(SaveQuestionSerializer):
    min_length = IntegerField(min_value=1, required=False, allow_null=True)
    max_length = IntegerField(min_value=1, required=False, allow_null=True)
    format_validators = ListField(child=CharField(), required=False)

    def validate(self, data):
        data["type"] = models.Question.TYPE_TEXT
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + [
            "min_length",
            "max_length",
            "placeholder",
            "hint_text",
            "format_validators",
        ]


class SaveTextareaQuestionSerializer(SaveQuestionSerializer):
    min_length = IntegerField(min_value=1, required=False, allow_null=True)
    max_length = IntegerField(min_value=1, required=False, allow_null=True)
    format_validators = ListField(child=CharField(), required=False)

    def validate(self, data):
        data["type"] = models.Question.TYPE_TEXTAREA
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + [
            "min_length",
            "max_length",
            "placeholder",
            "hint_text",
            "format_validators",
        ]


class SaveDateQuestionSerializer(SaveQuestionSerializer):
    def validate(self, data):
        data["type"] = models.Question.TYPE_DATE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ["hint_text"]


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
                modified_by_user=user.username,
                modified_by_group=user.group,
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
        fields = SaveQuestionSerializer.Meta.fields + ["options", "hint_text"]


class SaveChoiceQuestionSerializer(SaveQuestionOptionsMixin, SaveQuestionSerializer):
    options = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Option.objects.all(), many=True, required=True
    )

    def validate(self, data):
        data["type"] = models.Question.TYPE_CHOICE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ["options", "hint_text"]


class SaveDynamicChoiceQuestionSerializer(SaveQuestionSerializer):
    data_source = CharField()

    def validate(self, data):
        data["type"] = models.Question.TYPE_DYNAMIC_CHOICE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ["data_source", "hint_text"]


class SaveDynamicMultipleChoiceQuestionSerializer(SaveQuestionSerializer):
    data_source = CharField()

    def validate(self, data):
        data["type"] = models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ["data_source", "hint_text"]


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
        fields = SaveQuestionSerializer.Meta.fields + [
            "min_value",
            "max_value",
            "placeholder",
            "hint_text",
        ]


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
        fields = SaveQuestionSerializer.Meta.fields + [
            "min_value",
            "max_value",
            "placeholder",
            "hint_text",
        ]


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
        fields = SaveQuestionSerializer.Meta.fields + ["row_form", "hint_text"]


class SaveFormQuestionSerializer(SaveQuestionSerializer):
    sub_form = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Form.objects, required=True
    )

    def validate(self, data):
        data["type"] = models.Question.TYPE_FORM
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ["sub_form"]


class SaveFileQuestionSerializer(SaveQuestionSerializer):
    def validate(self, data):
        data["type"] = models.Question.TYPE_FILE
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + ["hint_text"]


class SaveStaticQuestionSerializer(SaveQuestionSerializer):
    static_content = CharField(required=False)

    def validate(self, data):
        data["type"] = models.Question.TYPE_STATIC
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = [
            "label",
            "slug",
            "info_text",
            "is_hidden",
            "meta",
            "is_archived",
            "static_content",
        ]


class SaveCalculatedFloatQuestionSerializer(SaveQuestionSerializer):
    calc_expression = QuestionJexlField(required=False)

    def validate(self, data):
        data["type"] = models.Question.TYPE_CALCULATED_FLOAT
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = SaveQuestionSerializer.Meta.fields + [
            "calc_expression",
            "hint_text",
        ]


class SaveActionButtonQuestionSerializer(SaveQuestionSerializer):
    action = ButtonActionField(required=True)
    color = ButtonColorField(required=True)
    validate_on_enter = BooleanField(required=True)

    def validate(self, data):
        data["type"] = models.Question.TYPE_ACTION_BUTTON
        return super().validate(data)

    class Meta(SaveQuestionSerializer.Meta):
        fields = [
            "label",
            "slug",
            "info_text",
            "is_hidden",
            "meta",
            "is_archived",
            "action",
            "color",
            "validate_on_enter",
        ]


class SaveOptionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["slug", "label", "is_archived", "meta"]
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
        fields = ["slug", "label", "source"]
        model = models.Option


class DocumentSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return domain_logic.SaveDocumentLogic.create(
            validated_data, user=self.context["request"].user
        )

    class Meta:
        model = models.Document
        fields = [
            "id",
            "form",
            "meta",
        ]
        extra_kwargs = {"id": {"read_only": False, "required": False}}


class SaveAnswerSerializer(serializers.ModelSerializer):
    def validate(self, data):
        data = domain_logic.SaveAnswerLogic.validate_for_save(
            data, self.context["request"].user, self.instance, True
        )
        return super().validate(data)

    @transaction.atomic
    def create(self, validated_data):
        return domain_logic.SaveAnswerLogic.create(
            validated_data, user=self.context["request"].user
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        return domain_logic.SaveAnswerLogic.update(instance, validated_data)

    class Meta:
        model = models.Answer
        fields = ["question", "document", "meta", "value"]


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

    class Meta(SaveAnswerSerializer.Meta):
        pass


class SaveDocumentFileAnswerSerializer(SaveAnswerSerializer):
    value = CharField(write_only=True, source="file", required=False)
    value_id = PrimaryKeyRelatedField(read_only=True, source="file", required=False)

    class Meta(SaveAnswerSerializer.Meta):
        fields = SaveAnswerSerializer.Meta.fields + [
            "value_id",
        ]


class RemoveAnswerSerializer(serializers.ModelSerializer):
    answer = PrimaryKeyRelatedField(
        queryset=models.Answer.objects.filter(document__isnull=False)
    )

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.delete()
        return instance

    class Meta:
        fields = [
            "answer",
        ]
        model = models.Answer


class SaveDefaultAnswerSerializer(serializers.ModelSerializer):
    def validate(self, data):
        return domain_logic.SaveDefaultAnswerLogic.validate_for_save(
            data, self.context["request"].user, self.instance, True
        )

    def create(self, validated_data):
        return domain_logic.SaveDefaultAnswerLogic.create(
            validated_data, self.context["request"].user
        )

    def update(self, instance, validated_data):
        return domain_logic.SaveDefaultAnswerLogic.update(instance, validated_data)

    class Meta:
        model = models.Answer
        fields = ["question", "meta", "value"]


class SaveDefaultStringAnswerSerializer(SaveDefaultAnswerSerializer):
    value = CharField(trim_whitespace=False, allow_blank=True, required=False)

    class Meta(SaveDefaultAnswerSerializer.Meta):
        pass


class SaveDefaultListAnswerSerializer(SaveDefaultAnswerSerializer):
    value = ListField(child=CharField(), required=False)

    class Meta(SaveDefaultAnswerSerializer.Meta):
        pass


class SaveDefaultIntegerAnswerSerializer(SaveDefaultAnswerSerializer):
    value = IntegerField(required=False)

    class Meta(SaveDefaultAnswerSerializer.Meta):
        pass


class SaveDefaultFloatAnswerSerializer(SaveDefaultAnswerSerializer):
    value = FloatField(required=False)

    class Meta(SaveDefaultAnswerSerializer.Meta):
        pass


class SaveDefaultDateAnswerSerializer(SaveDefaultAnswerSerializer):
    value = DateField(source="date", required=False)

    class Meta(SaveDefaultAnswerSerializer.Meta):
        pass


class SaveDefaultTableAnswerSerializer(SaveDefaultAnswerSerializer):
    value = serializers.GlobalIDPrimaryKeyRelatedField(
        source="documents",
        queryset=models.Document.objects,
        many=True,
        required=False,
        help_text="List of document IDs representing the rows in the table.",
    )

    class Meta(SaveDefaultAnswerSerializer.Meta):
        pass


class RemoveDefaultAnswerSerializer(serializers.ModelSerializer):
    question = PrimaryKeyRelatedField(queryset=models.Question.objects)

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.default_answer.delete()
        return instance

    class Meta:
        fields = [
            "question",
        ]
        model = models.Question


class RemoveDocumentSerializer(serializers.ModelSerializer):
    document = serializers.GlobalIDField(source="id")

    @transaction.atomic
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
        fields = ["document"]
        model = models.Document


class CopyDocumentSerializer(serializers.ModelSerializer):
    source = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Document.objects, required=True
    )

    @transaction.atomic
    def create(self, validated_data):
        return validated_data["source"].copy(
            family=None,
            user=self.context["request"].user,
        )

    class Meta:
        model = models.Document
        fields = ["source"]
