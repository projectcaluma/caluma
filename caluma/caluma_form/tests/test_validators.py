import pytest
from rest_framework.exceptions import ValidationError

from ...caluma_core.tests import extract_serializer_input_fields
from ...caluma_form.models import DynamicOption, Question
from .. import serializers, structure
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
    db,
    required_jexl,
    hidden_jexl,
    should_throw,
    form_question,
    document_factory,
    admin_user,
):
    form_question.question.is_required = required_jexl
    form_question.question.is_hidden = hidden_jexl
    form_question.question.save()

    document = document_factory(form=form_question.form)
    error_msg = f"Questions {form_question.question.slug} are required but not provided"
    if should_throw:
        with pytest.raises(ValidationError, match=error_msg):
            DocumentValidator().validate(document, admin_user)
    else:
        DocumentValidator().validate(document, admin_user)


@pytest.mark.parametrize(
    "question__type,question__is_required",
    [(Question.TYPE_FILE, "false"), (Question.TYPE_DATE, "false")],
)
def test_validate_special_fields(
    db, form_question, question, document_factory, answer_factory, admin_user
):
    document = document_factory(form=form_question.form)
    answer_factory(document=document, question=question)
    DocumentValidator().validate(document, admin_user)


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
    admin_user,
    settings,
):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyDataSource",
        "caluma.caluma_data_source.tests.data_sources.MyOtherDataSource",
    ]
    lookup_value = value
    if question.type == Question.TYPE_DYNAMIC_MULTIPLE_CHOICE and not value == 23:
        value = [value]

    document = document_factory(form=form_question.form)
    answer_factory(value=value, document=document, question=question)

    if valid:
        DocumentValidator().validate(document, admin_user)
        assert DynamicOption.objects.get(
            document=document, slug=lookup_value, question=question
        )
    else:
        with pytest.raises(ValidationError):
            DocumentValidator().validate(document, admin_user)


@pytest.mark.parametrize(
    "question__type",
    [Question.TYPE_DYNAMIC_CHOICE, Question.TYPE_DYNAMIC_MULTIPLE_CHOICE],
)
@pytest.mark.parametrize("question__data_source", ["MyDataSource"])
def test_validate_dynamic_option_exists(
    db,
    form_question,
    question,
    answer_factory,
    document_factory,
    dynamic_option_factory,
    admin_user,
    settings,
):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyDataSource"
    ]

    value = "foobar"
    document = document_factory(form=form_question.form)
    dynamic_option = dynamic_option_factory(
        document=document, question=question, slug=value, label="test"
    )

    if question.type == Question.TYPE_DYNAMIC_MULTIPLE_CHOICE:
        value = [value]
    answer_factory(question=question, value=value, document=document)

    assert DocumentValidator().validate(dynamic_option.document, admin_user) is None


@pytest.mark.parametrize(
    "required_jexl_main,required_jexl_sub,should_throw",
    [
        ("true", "false", True),
        ("'other_q_1'|answer == 'something'", "false", True),
        ("'other_q_1'|answer == 'something else'", "false", False),
        ("false", "false", False),
        ("'foo' in 'main_table_1'|answer|mapby('sub_question_a')", "false", True),
        ("'nothere' in 'main_table_1'|answer|mapby('sub_question_a')", "false", False),
        ("false", "'foo' == 'sub_question_a'|answer", True),
        ("false", "'bar' == 'sub_question_a'|answer", False),
        ("false", "'other_q_1'|answer == 'something'", True),
        ("false", "'other_q_1'|answer == 'something else'", False),
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
    admin_user,
):

    # F: main-form
    #     Q: main_table_1: table
    #        ROW_FORM
    #           Q: sub_question_a
    #           Q: sub_question_b (required_jexl_sub)
    #     Q: other_q_1
    #     Q: other_q_2 (required_jexl_main)

    main_form = form_factory(slug="main-form")
    main_table_question_1 = form_question_factory(
        form=main_form,
        question__type=Question.TYPE_TABLE,
        question__slug="main_table_1",
        question__is_required="true",
    )

    main_table_question_1.question.row_form = form_factory()
    main_table_question_1.question.save()

    sub_question_a = form_question_factory(
        form=main_table_question_1.question.row_form,
        question__type=Question.TYPE_TEXT,
        question__slug="sub_question_a",
    )
    sub_question_b = form_question_factory(
        form=main_table_question_1.question.row_form,
        question__type=Question.TYPE_TEXT,
        question__is_required=required_jexl_sub,
        question__slug="sub_question_b",
    )
    other_q_1 = form_question_factory(
        form=main_form,
        question__type=Question.TYPE_TEXT,
        question__slug="other_q_1",
        question__is_required="false",
    )

    other_q_2 = form_question_factory(
        form=main_form,
        question__type=Question.TYPE_TEXT,
        question__slug="other_q_2",
        question__is_required=required_jexl_main,
    )

    # MD
    #   - TA
    #       - RD1
    #           sqa:"foo"
    #   oq1:"something"

    main_document = document_factory(form=main_form)
    table_answer = answer_factory(
        document=main_document, question=main_table_question_1.question, value=None
    )

    row_document_1 = document_factory(form=main_table_question_1.question.row_form)
    answer_document_factory(document=row_document_1, answer=table_answer)

    answer_factory(
        question=sub_question_a.question, document=row_document_1, value="foo"
    )
    answer_factory(
        question=other_q_1.question, document=main_document, value="something"
    )

    if should_throw and required_jexl_sub.startswith("'fail'"):
        with pytest.raises(QuestionMissing):
            DocumentValidator().validate(main_document, admin_user)
    elif should_throw:
        q_slug = sub_question_b.question.slug
        if required_jexl_sub == "false":
            q_slug = other_q_2.question.slug
        error_msg = f"Questions {q_slug} are required but not provided"
        with pytest.raises(ValidationError, match=error_msg):
            DocumentValidator().validate(main_document, admin_user)
    else:
        DocumentValidator().validate(main_document, admin_user)


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
    db, question, valid, serializer_to_use, data_source_settings
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
        (Question.TYPE_TEXT, None, None),
        (Question.TYPE_TEXT, "", ""),
        (Question.TYPE_INTEGER, None, None),
        (Question.TYPE_FLOAT, None, None),
        (Question.TYPE_DATE, None, None),
        (Question.TYPE_FILE, None, None),
        (Question.TYPE_TEXTAREA, None, None),
    ],
)
@pytest.mark.parametrize("answer__date,answer__file", [(None, None)])
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

    struct = structure.FieldSet(document, document.form)
    field = struct.get_field(question.slug)
    answer_value = field.value() if field else field
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
            "Error while evaluating `is_required` expression on question q-slug: 'foo' in blah. The system log contains more information",
        ),
        (
            "q-slug",
            Question.TYPE_TEXT,
            "true",
            "'foo' in blah",
            "",
            "Error while evaluating `is_hidden` expression on question q-slug: 'foo' in blah. The system log contains more information",
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
    db, form_question, document, answer, question, exception_message, admin_user
):

    if exception_message is not None:
        with pytest.raises(RuntimeError) as exc:
            DocumentValidator().validate(document, admin_user)
        assert exc.value.args[0] == exception_message
    else:
        assert DocumentValidator().validate(document, admin_user) is None


def test_validate_required_integer_0(
    db, form_question, answer_factory, document_factory, admin_user
):
    form_question.question.is_required = "true"
    form_question.question.type = Question.TYPE_INTEGER
    form_question.question.save()

    document = document_factory(form=form_question.form)
    answer_factory(document=document, value=0, question=form_question.question)

    DocumentValidator().validate(document, admin_user)


@pytest.mark.parametrize(
    "question__type,answer__value",
    [
        (Question.TYPE_MULTIPLE_CHOICE, None),
        (Question.TYPE_MULTIPLE_CHOICE, []),
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, None),
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, []),
        (Question.TYPE_TEXT, None),
        (Question.TYPE_TEXT, ""),
        (Question.TYPE_INTEGER, None),
        (Question.TYPE_FLOAT, None),
        (Question.TYPE_DATE, None),
        (Question.TYPE_FILE, None),
        (Question.TYPE_TEXTAREA, None),
        (Question.TYPE_TABLE, None),
        (Question.TYPE_TABLE, []),
        (Question.TYPE_CHOICE, None),
        (Question.TYPE_DYNAMIC_CHOICE, None),
    ],
)
@pytest.mark.parametrize(
    "answer__date,answer__file,question__is_required", [(None, None, "true")]
)
def test_validate_required_empty_answers(
    db, admin_user, form_question, document, answer, question
):
    with pytest.raises(ValidationError):
        DocumentValidator().validate(document, admin_user)


@pytest.mark.parametrize("question__is_hidden", ["true", "false"])
@pytest.mark.parametrize(
    "question__type,question__configuration",
    [[Question.TYPE_FLOAT, {"min_value": 0, "max_value": 3}]],
)
def test_validate_hidden_field(
    db, form_question, document_factory, answer_factory, admin_user
):
    question = form_question.question
    document = document_factory(form=form_question.form)

    # answer is out of validation range so should fail
    answer_factory(question=question, document=document, value=4)

    if question.is_hidden == "true":
        assert DocumentValidator().validate(document, admin_user) is None
    else:
        with pytest.raises(ValidationError):
            DocumentValidator().validate(document, admin_user)


@pytest.mark.parametrize("hide_formquestion", [True, False])
def test_validate_hidden_subform(
    db,
    question_factory,
    form_factory,
    document_factory,
    form_question_factory,
    answer_factory,
    admin_user,
    hide_formquestion,
):
    # First, build our nested form:
    #     top_form
    #       \__ form_question # hidden or not/parametrized
    #            \__ sub_form
    #                 \__ sub_question
    #                 \__ sub_sub_fq  # always hidden. sub_sub_question should never be checked
    #                      \__ sub_sub_form
    #                          \__ sub_sub_question # required = true
    top_form = form_factory()
    sub_form = form_factory()
    form_question = question_factory(
        type=Question.TYPE_FORM,
        sub_form=sub_form,
        is_hidden=str(hide_formquestion).lower(),
        slug="form_question",
    )
    top_form.questions.add(form_question)
    sub_question = question_factory(
        type=Question.TYPE_FLOAT,
        configuration={"min_value": 0, "max_value": 3},
        slug="sub_question",
    )
    form_question_factory(form=sub_form, question=sub_question)

    sub_sub_form = form_factory(slug="sub_sub_form")
    sub_sub_fq = question_factory(
        type=Question.TYPE_FORM,
        sub_form=sub_sub_form,
        is_hidden="true",
        slug="sub_sub_fq",
    )
    form_question_factory(form=sub_form, question=sub_sub_fq)

    sub_sub_question = question_factory(
        is_required="true",
        is_hidden="false",
        slug="sub_sub_question",
        type=Question.TYPE_FLOAT,
        configuration={"min_value": 1, "max_value": 3},
    )
    form_question_factory(form=sub_sub_form, question=sub_sub_question)

    # Second, make a document. The answer for the sub_question should
    # be invalid to test if the hidden form question masks it properly.
    # We never answer sub_sub_question, thus making the document invalid
    # if it's wrongfully validated
    document = document_factory(form=top_form)
    answer_factory(question=sub_sub_question, document=document, value=4)

    if hide_formquestion:
        assert DocumentValidator().validate(document, admin_user) is None
    else:
        with pytest.raises(ValidationError) as excinfo:
            DocumentValidator().validate(document, admin_user)
        # Verify that the sub_sub_question is not the cause of the exception:
        # it should not be checked at all because it's parent is always hidden
        assert excinfo.match(r"Questions \bsub_question\s.* required but not provided.")

        # can't do `not excinfo.match()` as it throws an AssertionError itself
        # if it can't match :()
        assert "sub_sub_question" not in str(excinfo.value.detail)


@pytest.mark.parametrize("answer_value", ["foo", "bar"])
def test_dependent_question_is_hidden(
    db,
    question_factory,
    form_factory,
    document_factory,
    form_question_factory,
    answer_factory,
    answer_value,
    admin_user,
):
    form = form_factory()
    q1 = question_factory(is_hidden="false", type=Question.TYPE_TEXT)
    q2 = question_factory(
        is_hidden=f"'{q1.slug}'|answer=='foo'",
        type=Question.TYPE_TEXT,
        is_required="true",
    )
    q3 = question_factory(
        is_hidden=f"'{q2.slug}'|answer=='bar'",
        is_required="true",
        type=Question.TYPE_TEXT,
    )
    form_question_factory(form=form, question=q1)
    form_question_factory(form=form, question=q2)
    form_question_factory(form=form, question=q3)

    document = document_factory(form=form)
    answer_factory(question=q1, document=document, value=answer_value)
    answer_factory(question=q2, document=document, value="foo")

    if answer_value == "foo":
        # Answer to q1's value is "foo", so q2 is hidden. This means
        # that q3 should be hidden and not required as well
        assert DocumentValidator().validate(document, admin_user) is None
    else:
        # a1's value is "bar", so q2 is visible. This means
        # that q3 should also be visible and required
        with pytest.raises(ValidationError):
            DocumentValidator().validate(document, admin_user)


@pytest.mark.parametrize("question__type", ["file"])
@pytest.mark.parametrize("question__is_required", ["true"])
@pytest.mark.parametrize("question__is_hidden", ["false"])
def test_required_file(db, question, form, document, answer, admin_user, form_question):
    # verify some assumptions
    assert document.form == form
    assert answer.document == document
    assert form in question.forms.all()
    assert answer.file

    # remove the file
    the_file = answer.file
    answer.file = None
    answer.save()

    # ensure validation fails with no `file` value
    with pytest.raises(ValidationError):
        DocumentValidator().validate(document, admin_user)

    # put the file back
    answer.file = the_file
    answer.save()

    # then, validation must pass
    assert DocumentValidator().validate(document, admin_user) is None


def test_validate_missing_in_subform(
    db,
    question_factory,
    form_factory,
    document_factory,
    form_question_factory,
    answer_factory,
    admin_user,
):
    # First, build our nested form:
    #     top_form
    #       \__ form_question # not required
    #            \__ sub_form
    #                 \__ sub_question# required, but not filled
    top_form = form_factory()
    sub_form = form_factory()

    # form question is not required
    form_question = question_factory(
        type=Question.TYPE_FORM,
        sub_form=sub_form,
        is_hidden="false",
        is_required="false",
        slug="form_question",
    )
    form_question_factory(form=top_form, question=form_question)

    # sub question is required
    sub_question = question_factory(
        type=Question.TYPE_FLOAT,
        configuration={"min_value": 0, "max_value": 3},
        is_hidden="false",
        is_required="true",
        slug="sub_question",
    )
    form_question_factory(form=sub_form, question=sub_question)

    # Second, make a document.
    # the sub question remains unanswered, which should raise an error
    document = document_factory(form=top_form)

    with pytest.raises(ValidationError) as excinfo:
        DocumentValidator().validate(document, admin_user)

    # Verify that the sub_sub_question is not the cause of the exception:
    # it should not be checked at all because it's parent is always hidden
    assert excinfo.match(r"Questions \bsub_question\s.* required but not provided.")


@pytest.mark.parametrize("table_required", [True, False])
def test_validate_missing_in_table(
    db,
    question_factory,
    form_factory,
    document_factory,
    form_question_factory,
    answer_document_factory,
    answer_factory,
    table_required,
    admin_user,
):
    # First, build our nested form:
    #     top_form
    #       \__ table_question # requiredness parametrized
    #            \__ sub_form
    #                 \__ sub_question1 # required and filled
    #                 \__ sub_question2 # required, but not filled
    top_form = form_factory()
    sub_form = form_factory()

    # form question is not required
    table_question = question_factory(
        type=Question.TYPE_TABLE,
        row_form=sub_form,
        is_hidden="false",
        is_required=str(table_required).lower(),
        slug="table_question",
    )
    form_question_factory(form=top_form, question=table_question)

    # sub question1 is NOT required
    sub_question1 = question_factory(
        type=Question.TYPE_TEXT,
        is_hidden="false",
        is_required="true",
        slug="sub_question1",
    )
    # sub question1 is required
    sub_question2 = question_factory(
        type=Question.TYPE_TEXT,
        is_hidden="false",
        is_required="true",
        slug="sub_question2",
    )
    form_question_factory(form=sub_form, question=sub_question1)
    form_question_factory(form=sub_form, question=sub_question2)

    # Second, make a document.
    # it has one row, but the answer to question2 is missing
    document = document_factory(form=top_form)
    table_ans = answer_factory(document=document, question=table_question)

    if table_required:
        # Table required. But we only fill it partially, this
        # should raise an error
        row_doc = document_factory(form=sub_form)
        answer_document_factory(answer=table_ans, document=row_doc)
        row_doc.answers.create(question=sub_question1, value="hi")

        with pytest.raises(ValidationError) as excinfo:
            DocumentValidator().validate(document, admin_user)
        # Verify that the sub_sub_question is not the cause of the exception:
        # it should not be checked at all because it's parent is always hidden
        assert excinfo.match(
            r"Questions \bsub_question2\s.* required but not provided."
        )

    else:
        # should not raise
        DocumentValidator().validate(document, admin_user)


@pytest.mark.parametrize(
    "column_is_hidden,expect_error",
    [("form == 'topform'", False), ("form == 'rowform'", True)],
)
def test_validate_form_in_table(
    db,
    question_factory,
    form_factory,
    document_factory,
    form_question_factory,
    answer_document_factory,
    answer_factory,
    column_is_hidden,
    expect_error,
    admin_user,
):
    # First, build our nested form:
    #     top_form
    #       \__ table_question # requiredness parametrized
    #            \__ sub_form
    #                 \__ sub_question1 # required and filled
    #                 \__ sub_question2 # required, but not filled
    top_form = form_factory(slug="topform")
    sub_form = form_factory(slug="rowform")

    # form question is not required
    table_question = question_factory(
        type=Question.TYPE_TABLE,
        row_form=sub_form,
        is_required="true",
        is_hidden="false",
        slug="table_question",
    )
    form_question_factory(form=top_form, question=table_question)

    # sub question1 is required and filled
    sub_question1 = question_factory(
        type=Question.TYPE_TEXT,
        is_required="true",
        is_hidden="false",
        slug="sub_question1",
    )
    # sub question2 depends on the form, is NOT filled
    sub_question2 = question_factory(
        type=Question.TYPE_TEXT,
        is_required="true",
        is_hidden=column_is_hidden,
        slug="sub_question2",
    )
    form_question_factory(form=sub_form, question=sub_question1)
    form_question_factory(form=sub_form, question=sub_question2)

    # Second, make a document.
    # it has one row, but the answer to question2 is missing
    document = document_factory(form=top_form)
    table_ans = answer_factory(document=document, question=table_question)

    row_doc = document_factory(form=sub_form)
    answer_document_factory(answer=table_ans, document=row_doc)
    row_doc.answers.create(question=sub_question1, value="hi")

    if expect_error:
        # column "sub_question2" required, but won't be answered.
        # Should raise an error

        with pytest.raises(ValidationError) as excinfo:
            DocumentValidator().validate(document, admin_user)
        # Verify that the sub_sub_question is not the cause of the exception:
        # it should not be checked at all because it's parent is always hidden
        assert excinfo.match(
            r"Questions \bsub_question2\s.* required but not provided."
        )

    else:
        # Should not raise, as the "form" referenced by the
        # question's jexl is the rowform, which is wrong
        DocumentValidator().validate(document, admin_user)
