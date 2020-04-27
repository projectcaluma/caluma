import pytest

from .. import structure, validators
from ..jexl import QuestionJexl, QuestionMissing
from ..models import Question


@pytest.mark.parametrize(
    "expression,num_errors",
    [
        # correct case
        ("\"question-slug\"|answer|mapby('key')", 0),
        # invalid subject type
        ("100|answer", 1),
        # two invalid subject types
        ('["test"]|answer || 1.0|answer', 2),
        # invalid operator
        ("'question-slug1'|answer &&& 'question-slug2'|answer", 1),
    ],
)
def test_question_jexl_validate(expression, num_errors):
    jexl = QuestionJexl()
    assert len(list(jexl.validate(expression))) == num_errors


@pytest.mark.parametrize(
    "expression,result",
    [
        ("[{ key: 1 }]|mapby('key')", [1]),
        ("[{ otherkey: 1 }]|mapby('key')", [None]),
        ("[]|mapby('key')", []),
    ],
)
def test_mapby_operator(expression, result):
    assert QuestionJexl().evaluate(expression) == result


@pytest.mark.parametrize(
    "expression,result",
    [
        ("[1,2] intersects [2,3]", True),
        ("[1,2] intersects [3,4]", False),
        ("[] intersects []", False),
        ("[1] intersects []", False),
        ("['foo'] intersects ['bar', 'bazz']", False),
        ("['foo'] intersects ['foo', 'foo']", True),
        ("[1] intersects [1] && [2] intersects [2]", True),
        ("[2] intersects [1] + [2]", True),
    ],
)
def test_intersects_operator(expression, result):
    assert QuestionJexl().evaluate(expression) == result


@pytest.mark.parametrize("form__slug", ["f-main-slug"])
def test_jexl_form(db, form):
    answer_by_question = {
        "a1": {"value": "A1", "form": form},
        "b1": {"value": "B1", "form": form},
    }

    assert (
        QuestionJexl({"answers": answer_by_question, "form": form}).evaluate("form")
        == "f-main-slug"
    )


def test_all_deps_hidden(db, form, document_factory, form_question_factory):
    q1 = form_question_factory(form=form, question__is_hidden="true").question
    q2 = form_question_factory(
        form=form,
        question__is_hidden=f"'{q1.slug}'|answer=='blah'",
        question__is_required=f"'{q1.slug}'|answer=='blah'",
    ).question
    document = document_factory(form=form)

    qj = QuestionJexl(
        {
            "document": document,
            "answers": {},
            "form": form,
            "structure": structure.FieldSet(document, document.form),
        }
    )
    assert qj.is_hidden(q2)
    assert not qj.is_required(structure.Field(document, document.form, q2))


@pytest.mark.parametrize("fq_is_hidden", ["true", "false"])
def test_indirectly_hidden_dependency(
    db,
    form_question_factory,
    form_factory,
    question_factory,
    document_factory,
    answer_factory,
    info,
    fq_is_hidden,
):
    # Questions can not only be hidden by evaluating their is_hidden expression
    # but also if they're part of a subform, where the containing form question
    # is hidden.
    #
    # Showcase form to demonstrate this (f:form, q:question, d:document, a:answer):
    # f:topform
    #    q:formquestionbranch - hidden=false
    #      f:subformbranch
    #         q:depquestion2 - required = 'subquestion2'|answer=='bluh'
    #    q:formquestion - hidden=variable
    #      f:subform
    #         q:subquestion1 - hidden=false
    #         q:subquestion2 - hidden=false
    #   q:depquestion1 - required = 'subquestion1'|answer=='blah'
    #
    # d:topdoc f=topform
    #    a:subanswer1 q=subquestion1, value='blah'
    #    a:subanswer2 q=subquestion2, value='bluh'
    #    (depquestion1 and depquestion2 have no answers, as they're indirectly not required)
    #
    # Note: The above structure shows the actual "feature" case.
    # We also test with `subquestion` not hidden, to ensure both ways
    # work correctly

    # Build the form first...
    topform = form_factory(slug="top")
    subformbranch = form_factory(slug="subform")
    subform = form_factory(slug="subformbranch")

    formquestion = question_factory(
        type=Question.TYPE_FORM,
        is_hidden=fq_is_hidden,
        sub_form=subform,
        slug="topformquestion",
    )
    formquestionbranch = question_factory(
        type=Question.TYPE_FORM,
        is_hidden="false",
        sub_form=subformbranch,
        slug="topformquestionbranch",
    )
    subquestion1 = question_factory(
        type=Question.TYPE_INTEGER, is_hidden="false", slug="subquestion1"
    )
    subquestion2 = question_factory(
        type=Question.TYPE_INTEGER, is_hidden="false", slug="subquestion2"
    )
    depquestion1 = question_factory(
        type=Question.TYPE_INTEGER,
        is_required="'subquestion1'|answer=='blah'",
        slug="depquestion1",
    )
    depquestion2 = question_factory(
        type=Question.TYPE_INTEGER,
        is_required="'subquestion2'|answer=='bluh'",
        slug="depquestion2",
    )
    form_question_factory(form=topform, question=formquestion)
    form_question_factory(form=topform, question=formquestionbranch)
    form_question_factory(form=topform, question=depquestion1)

    form_question_factory(form=subformbranch, question=depquestion2)

    form_question_factory(form=subform, question=subquestion1)
    form_question_factory(form=subform, question=subquestion2)

    # ... then build the document
    topdoc = document_factory(form=topform)
    answer_factory(document=topdoc, question=subquestion1, value="blah")
    answer_factory(document=topdoc, question=subquestion2, value="bluh")

    validator = validators.DocumentValidator()

    if fq_is_hidden == "true":
        # parent is hidden, required question cannot be
        # shown, thus is implicitly hidden
        validator.validate(topdoc, info)
        assert True  # above did not fail
    else:
        with pytest.raises(validators.CustomValidationError):
            validator.validate(topdoc, info)


def test_reference_missing_question(
    db, form_question_factory, form_factory, question_factory, document_factory, info
):
    topform = form_factory(slug="top")

    depquestion = question_factory(
        type=Question.TYPE_INTEGER, is_hidden="'subquestion-missing'|answer=='blah'"
    )
    form_question_factory(form=topform, question=depquestion)

    # ... then build the document
    topdoc = document_factory(form=topform)
    validator = validators.DocumentValidator()

    with pytest.raises(QuestionMissing):
        validator.validate(topdoc, info)


@pytest.mark.parametrize(
    "question,expr,expectation,features",
    [
        ("sub_question", "info.form == 'sub_form'", True, "subform"),
        ("sub_question", "info.parent.form == 'top_form'", True, "subform"),
        ("column", "info.parent.form == 'top_form'", True, "table"),
        ("column", "info.root.form == 'top_form'", True, "table"),
    ],
)
def test_new_jexl_expressions(
    question, expr, expectation, features, info, form_and_document
):
    """Evaluate a JEXL expression in the context of a full document.

    The given JEXL expression is evaluated in the context of the given
    question within a structured document. The expression's value (boolean)
    is then returned. The document is generated with the following structure:

    * form: top_form
       * question: top_question
       * question: table [enabled by putting 'table' in features param]
           * row_form: row_form
               * question: column
       * question: form_question [enabled by putting 'subform' in features param]
           * sub_form: sub_form
               * question: sub_question
    """

    use_table = "table" in features
    use_subform = "subform" in features

    form, document, questions, answers = form_and_document(
        use_table=use_table, use_subform=use_subform
    )

    # expression test method: we delete an answer and set it's is_hidden
    # to an expression to be tested. If the expression evaluates to True,
    # we won't have a ValidationError.
    answers[question].delete()
    questions[question].is_hidden = expr
    questions[question].save()

    def do_check():
        validator = validators.DocumentValidator()
        try:
            validator.validate(document, info)
            return True
        except validators.CustomValidationError:  # pragma: no cover
            return False

    assert do_check() == expectation


def test_answer_transform_on_hidden_question(info, form_and_document):
    # Bug test: When a JEXL expression references two answers, and one of them
    # is hidden, the `answer` transform must return None for the hidden question
    # to ensure correct evaluation.

    form, document, questions, answers = form_and_document(
        use_table=True, use_subform=True
    )

    # the "sub_question" question is hidden (no magic). This means
    # it's "answer" transform should always return None
    questions["sub_question"].is_hidden = "true"
    questions["sub_question"].is_required = "true"
    questions["sub_question"].save()

    # sub_question and top_question are referenced in a JEXL expresison later on
    answers["sub_question"].value = "hello"
    answers["sub_question"].save()
    answers["top_question"].value = "xyz"
    answers["top_question"].save()

    # the `column` question is used to evaluate the expression via `is_required`:
    # The required state depends on two questions, so we can check the expression's
    # result by checking whether the validator throws an exception.
    answers["column"].delete()

    validator = validators.DocumentValidator()

    # expression references two other questions, so it will still be evaluated
    # even if one question is hidden.
    # This specific expression evaluates to `True` only if the `answer` transform
    # works correctly
    questions[
        "column"
    ].is_required = "'sub_question'|answer == null && 'top_question'|answer=='xyz'"
    questions["column"].is_hidden = "false"
    questions["column"].save()

    with pytest.raises(validators.CustomValidationError):
        validator.validate(document, info)

    # Counter-Test to the `expect_fail` case: Ensure the answer transform still works
    questions["column"].is_required = "'sub_question'|answer == 'hello'"
    questions["column"].is_hidden = "false"
    questions["column"].save()

    assert validator.validate(document, info) is None


@pytest.mark.parametrize(
    "question_type,expected_value",
    [
        (Question.TYPE_MULTIPLE_CHOICE, []),
        (Question.TYPE_INTEGER, None),
        (Question.TYPE_FLOAT, None),
        (Question.TYPE_DATE, None),
        (Question.TYPE_CHOICE, None),
        (Question.TYPE_TEXTAREA, None),
        (Question.TYPE_TEXT, None),
        (Question.TYPE_TABLE, []),
        (Question.TYPE_FILE, None),
        (Question.TYPE_DYNAMIC_CHOICE, None),
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, []),
        # Those should not appear in a JEXL answer transform
        # (Question.TYPE_FORM,None),
        # (Question.TYPE_STATIC,None),
    ],
)
def test_answer_transform_on_hidden_question_types(
    info, form_and_document, question_type, expected_value
):
    form, document, questions, answers = form_and_document(
        use_table=True, use_subform=True
    )

    questions[
        "form_question"
    ].is_hidden = (
        f"'top_question'|answer == {expected_value} && 'table'|answer|mapby('column')"
    )
    questions["form_question"].save()

    questions["top_question"].is_hidden = "true"
    questions["top_question"].type = question_type
    questions["top_question"].save()

    qj = QuestionJexl(
        {
            "document": document,
            "answers": answers,
            "form": form,
            "structure": structure.FieldSet(document, document.form),
        }
    )

    assert qj.is_hidden(questions["form_question"])


@pytest.mark.parametrize(
    "jexl_field,expr",
    [
        ("is_required", "('column'|answer == 5)"),
        ("is_hidden", "('column'|answer > 10)"),
    ],
)
def test_answer_transform_in_tables(
    info,
    form_and_document,
    form_question_factory,
    jexl_field,
    expr,
    answer_document_factory,
):

    form, document, questions, answers = form_and_document(
        use_table=True, use_subform=False
    )

    table_question = questions["table_question"]

    col2_question = form_question_factory(
        **{
            "form": table_question.row_form,
            "question__slug": "column2",
            "question__is_hidden": "false",
            "question__is_required": "true",
            # this overrwrites above "default values"
            f"question__{jexl_field}": expr,
        }
    ).question
    assert getattr(col2_question, jexl_field) == expr

    table_answer = answers["table_question"]

    row2_doc = answer_document_factory(
        answer=table_answer, document__form=table_question.row_form, sort=10
    ).document

    # Second row has an answer that triggers the transform and implies a validation error.
    # This will wrongfully succeed if the answer value comes from the wrong row
    row2_doc.answers.create(question_id="column", value=5)

    validator = validators.DocumentValidator()
    # we expect this to fail, as in the second row, the 'column' answer is 5,
    # so 'column2' should be required
    with pytest.raises(validators.CustomValidationError):
        validator.validate(document, info)
