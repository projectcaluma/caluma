import pytest
from rest_framework.exceptions import ValidationError

from ...core.tests import extract_serializer_input_fields
from ...form.models import DynamicOption, Question
from .. import serializers
from ..jexl import QuestionMissing
from ..validators import DocumentValidator, QuestionValidator


@pytest.mark.parametrize(
    "required_jexl,hidden_jexl,should_throw",
    [
        ("false", "true", False),
        ("false", "false", False),
        ("true", "true", False),
        ("true", "false", True),
    ],
)
@pytest.mark.parametrize("question__type", [Question.TYPE_TEXT])
def test_validate_hidden_required_field(
    db, required_jexl, hidden_jexl, should_throw, form_question, document_factory, info
):
    form_question.question.is_required = required_jexl
    form_question.question.is_hidden = hidden_jexl
    form_question.question.save()

    document = document_factory(form=form_question.form)
    error_msg = f"Questions {form_question.question.slug} are required but not provided"
    if should_throw:
        with pytest.raises(ValidationError, match=error_msg):
            DocumentValidator().validate(document, info)
    else:
        DocumentValidator().validate(document, info)


@pytest.mark.parametrize(
    "question__type,question__is_required",
    [(Question.TYPE_FILE, "false"), (Question.TYPE_DATE, "false")],
)
def test_validate_special_fields(
    db, form_question, question, document_factory, answer_factory, info
):
    document = document_factory(form=form_question.form)
    answer_factory(document=document, question=question)
    DocumentValidator().validate(document, info)


@pytest.mark.parametrize(
    "question__data_source,value,valid",
    [
        ("MyDataSource", "5.5", True),
        ("MyDataSource", 5.5, False),
        ("MyOtherDataSource", "5.5", True),
        ("MyOtherDataSource", 5.5, False),
        ("MyOtherDataSource", 23, False),
        ("MyDataSource", "not in data", False),
        ("MyOtherDataSource", "not in data", True),
    ],
)
@pytest.mark.parametrize(
    "question__type",
    [Question.TYPE_DYNAMIC_CHOICE, Question.TYPE_DYNAMIC_MULTIPLE_CHOICE],
)
def test_validate_dynamic_options(
    db,
    form_question,
    question,
    value,
    valid,
    document_factory,
    answer_factory,
    info,
    settings,
):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.data_source.tests.data_sources.MyDataSource",
        "caluma.data_source.tests.data_sources.MyOtherDataSource",
    ]
    lookup_value = value
    if question.type == Question.TYPE_DYNAMIC_MULTIPLE_CHOICE and not value == 23:
        value = [value]

    document = document_factory(form=form_question.form)
    answer_factory(value=value, document=document, question=question)

    if valid:
        DocumentValidator().validate(document, info)
        assert DynamicOption.objects.get(
            document=document, question=question, value=lookup_value
        )
    else:
        with pytest.raises(ValidationError):
            DocumentValidator().validate(document, info)


@pytest.mark.parametrize(
    "required_jexl,should_throw", [("true", True), ("false", False)]
)
def test_validate_nested_form(
    db,
    required_jexl,
    should_throw,
    form_question_factory,
    document_factory,
    answer_factory,
    info,
):
    sub_form_question_1 = form_question_factory(
        form__slug="sub_1",
        question__type=Question.TYPE_TEXT,
        question__slug="sub_1_question_1",
    )
    sub_form_question_2 = form_question_factory(
        form__slug="sub_2",
        question__type=Question.TYPE_TEXT,
        question__is_required=required_jexl,
        question__slug="sub_2_question_1",
    )

    main_form_question_1 = form_question_factory(
        question__type=Question.TYPE_FORM,
        question__sub_form=sub_form_question_1.form,
        question__slug="sub_1",
        question__is_required="false",
    )
    form_question_factory(
        form=main_form_question_1.form,
        question__type=Question.TYPE_FORM,
        question__sub_form=sub_form_question_2.form,
        question__slug="sub_2",
        question__is_required="false",
    )

    main_document = document_factory(form=main_form_question_1.form)

    answer_factory(
        document=main_document, question=sub_form_question_1.question, value="foo"
    )

    if should_throw:
        error_msg = f"Questions {sub_form_question_2.question.slug} are required but not provided"
        with pytest.raises(ValidationError, match=error_msg):
            DocumentValidator().validate(main_document, info)
    else:
        DocumentValidator().validate(main_document, info)


@pytest.mark.parametrize(
    "required_jexl_main,required_jexl_sub,should_throw",
    [
        ("true", "false", True),
        ("'other_q_1'|answer == 'something'", "false", False),
        ("false", "false", False),
        ("'foo' in 'main_table_1'|answer|mapby('sub_1_question_a')", "false", True),
        (
            "'nothere' in 'main_table_1'|answer|mapby('sub_1_question_a')",
            "false",
            False,
        ),
        ("false", "'foo' == 'sub_1_question_a'|answer", True),
        ("false", "'bar' == 'sub_1_question_a'|answer", False),
        ("false", "'something' == 'other_q_1'|answer", True),
        ("false", "'fail' == 'no-question-slug'|answer", True),
    ],
)
def test_validate_table(
    db,
    required_jexl_main,
    required_jexl_sub,
    should_throw,
    answer_document_factory,
    form_factory,
    form_question_factory,
    document_factory,
    answer_factory,
    info,
):
    main_table_question_1 = form_question_factory(
        form__slug="main-form",
        question__type=Question.TYPE_TABLE,
        question__slug="main_table_1",
        question__is_required="true",
    )

    main_table_question_1.question.sub_form = form_factory()

    sub_question_a = form_question_factory(
        form=main_table_question_1.question.sub_form,
        question__type=Question.TYPE_TEXT,
        question__slug="sub_1_question_a",
    )
    sub_question_b = form_question_factory(
        form=main_table_question_1.question.sub_form,
        question__type=Question.TYPE_TEXT,
        question__is_required=required_jexl_sub,
        question__slug="sub_2_question_b",
    )

    main_document = document_factory(form=main_table_question_1.form)
    table_answer = answer_factory(
        document=main_document, question=main_table_question_1.question, value=None
    )
    row_document_1 = document_factory(form=main_table_question_1.question.sub_form)
    answer_factory(
        question=sub_question_a.question, document=row_document_1, value="foo"
    )
    answer_document_factory(document=row_document_1, answer=table_answer)

    other_q_1 = form_question_factory(
        form=main_table_question_1.form,
        question__type=Question.TYPE_TEXT,
        question__slug="other_q_1",
        question__is_required="false",
    )

    other_q_2 = form_question_factory(
        form=main_table_question_1.form,
        question__type=Question.TYPE_TEXT,
        question__slug="other_q_2",
        question__is_required=required_jexl_main,
    )

    answer_factory(
        question=other_q_1.question, document=row_document_1, value="something"
    )

    if should_throw and required_jexl_sub.startswith("'fail'"):
        with pytest.raises(QuestionMissing):
            DocumentValidator().validate(main_document, info)
    elif should_throw:
        q_slug = sub_question_b.question.slug
        if required_jexl_sub == "false":
            q_slug = other_q_2.question.slug
        error_msg = f"Questions {q_slug} are required but not provided"
        with pytest.raises(ValidationError, match=error_msg):
            DocumentValidator().validate(main_document, info)
    else:
        DocumentValidator().validate(main_document, info)


@pytest.mark.parametrize(
    "question__data_source,valid", [("MyDataSource", True), ("NotADataSource", False)]
)
@pytest.mark.parametrize(
    "question__type,serializer_to_use",
    [
        (Question.TYPE_DYNAMIC_CHOICE, "SaveDynamicChoiceQuestionSerializer"),
        (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            "SaveDynamicMultipleChoiceQuestionSerializer",
        ),
    ],
)
def test_validate_data_source(
    db, question, valid, info, serializer_to_use, data_source_settings
):
    serializer = getattr(serializers, serializer_to_use)

    data = extract_serializer_input_fields(serializer, question)
    data["type"] = question.type

    if valid:
        QuestionValidator().validate(data)
    else:
        with pytest.raises(ValidationError):
            QuestionValidator().validate(data)


@pytest.mark.parametrize(
    "question__type,answer__value,expected_value",
    [
        (Question.TYPE_MULTIPLE_CHOICE, None, []),
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, None, []),
    ],
)
def test_validate_empty_answers(
    db,
    form_question,
    document,
    answer,
    question,
    document_factory,
    answer_factory,
    expected_value,
):

    answer_value = DocumentValidator()._get_answer_value(answer, document)
    assert answer_value == expected_value


@pytest.mark.parametrize(
    "question__slug,question__type,question__is_required,question__is_hidden,answer__value,exception_message",
    [
        (
            "q-slug",
            Question.TYPE_TEXT,
            "'foo' in blah",
            "false",
            "",
            "Error while evaluating 'is_required' expression on question q-slug: 'foo' in blah. The system log contains more information",
        ),
        (
            "q-slug",
            Question.TYPE_TEXT,
            "true",
            "'foo' in blah",
            "",
            "Error while evaluating 'is_hidden' expression on question q-slug: 'foo' in blah. The system log contains more information",
        ),
        (
            "q-slug",
            Question.TYPE_TEXT,
            "'value' == 'q-slug'|answer",
            "false",
            "value",
            None,
        ),
    ],
)
def test_validate_invalid_jexl(
    db, form_question, document, answer, question, exception_message, info
):

    if exception_message is not None:
        with pytest.raises(RuntimeError) as exc:
            DocumentValidator().validate(document, info)
        assert exc.value.args[0] == exception_message
    else:
        assert DocumentValidator().validate(document, info) is None


def test_validate_required_integer_0(
    db, form_question, answer_factory, document_factory, info
):
    form_question.question.is_required = "true"
    form_question.question.type = Question.TYPE_INTEGER
    form_question.question.save()

    document = document_factory(form=form_question.form)
    answer_factory(document=document, value=0, question=form_question.question)

    DocumentValidator().validate(document, info)
