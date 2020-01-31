import pytest

from .. import structure, validators
from ..jexl import QuestionJexl, QuestionMissing
from ..models import Question


@pytest.mark.parametrize(
    "expression,num_errors",
    [
        # correct case
        ('"question-slug"|answer|mapby', 0),
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
    assert not qj.is_required(q2)


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
    # Showcase form to demonstrate this (f: form, q:question, d:document, a:answer):
    # f:topform
    #   q:formquestion - hidden=true
    #      f:subform
    #         q:subquestion - hidden=false
    #   q:depquestion - required = subquestion|answer=='blah'
    #
    # d:topdoc f=topform
    #    a:subanswer q=subquestion, value='blah'
    #    (depquestion has no answer, as it's indirectly not required)
    #
    # Note: The above structure shows the actual "feature" case.
    # We also test with `subquestion` not hidden, to ensure both ways
    # work correctly

    # Build the form first...
    topform = form_factory(slug="top")
    subform = form_factory(slug="subform")

    formquestion = question_factory(
        type=Question.TYPE_FORM, is_hidden=fq_is_hidden, sub_form=subform
    )
    subquestion = question_factory(
        type=Question.TYPE_INTEGER, is_hidden="false", slug="subquestion"
    )
    depquestion = question_factory(
        type=Question.TYPE_INTEGER, is_required="'subquestion'|answer=='blah'"
    )
    form_question_factory(form=topform, question=formquestion)
    form_question_factory(form=topform, question=depquestion)

    form_question_factory(form=subform, question=subquestion)

    # ... then build the document
    topdoc = document_factory(form=topform)
    answer_factory(document=topdoc, question=subquestion, value="blah")

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
