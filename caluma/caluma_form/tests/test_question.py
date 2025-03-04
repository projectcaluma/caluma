import pytest
from graphql_relay import to_global_id

from caluma.caluma_core.relay import extract_global_id
from caluma.caluma_core.tests import (
    extract_global_id_input_fields,
    extract_serializer_input_fields,
)

from .. import api, domain_logic, models, serializers
from ..jexl import QuestionJexl


@pytest.mark.parametrize(
    "question__type,question__configuration,question__data_source,question__format_validators",
    [
        (models.Question.TYPE_INTEGER, {"max_value": 10, "min_value": 0}, None, []),
        (
            models.Question.TYPE_FLOAT,
            {"max_value": 1.0, "min_value": 0.0, "step": 0.2},
            None,
            [],
        ),
        (models.Question.TYPE_FLOAT, {}, None, []),
        (models.Question.TYPE_DATE, {}, None, []),
        (models.Question.TYPE_TEXT, {"min_length": 10}, None, ["email"]),
        (models.Question.TYPE_TEXTAREA, {"max_length": 10}, None, []),
        (models.Question.TYPE_CHOICE, {}, None, []),
        (models.Question.TYPE_MULTIPLE_CHOICE, {}, None, []),
        (models.Question.TYPE_FORM, {}, None, []),
        (models.Question.TYPE_FILES, {}, None, []),
        (models.Question.TYPE_DYNAMIC_CHOICE, {}, "MyDataSource", []),
        (models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, {}, "MyDataSource", []),
        (models.Question.TYPE_STATIC, {}, None, []),
        (models.Question.TYPE_CALCULATED_FLOAT, {}, None, []),
        (models.Question.TYPE_ACTION_BUTTON, {}, None, []),
    ],
)
def test_query_all_questions(
    schema_executor,
    db,
    snapshot,
    question,
    form,
    form_question_factory,
    question_option,
    data_source_settings,
):
    form_question_factory.create(form=form)

    query = """
        query AllQuestionsQuery($search: String, $forms: [ID]) {
          allQuestions(filter: [{isArchived: false}, {search: $search}, {excludeForms: $forms}]) {
            totalCount
            edges {
              node {
                id
                __typename
                slug
                label
                meta
                infoText
                ... on TextQuestion {
                  minLength
                  maxLength
                  placeholder
                  hintText
                  formatValidators {
                    edges {
                      node {
                        slug
                        name
                        regex
                        errorMsg
                      }
                    }
                  }
                }
                ... on TextareaQuestion {
                  minLength
                  maxLength
                  placeholder
                  hintText
                  formatValidators {
                    edges {
                      node {
                        slug
                        name
                        regex
                        errorMsg
                      }
                    }
                  }
                }
                ... on DateQuestion {
                  hintText
                }
                ... on FloatQuestion {
                  floatMinValue: minValue
                  floatMaxValue: maxValue
                  floatStep: step
                  placeholder
                  hintText
                }
                ... on IntegerQuestion {
                  integerMinValue: minValue
                  integerMaxValue: maxValue
                  placeholder
                  hintText
                }
                ... on MultipleChoiceQuestion {
                  hintText
                  options {
                    totalCount
                    edges {
                      node {
                        slug
                      }
                    }
                  }
                }
                ... on ChoiceQuestion {
                  hintText
                  options {
                    totalCount
                    edges {
                      node {
                        slug
                      }
                    }
                  }
                }
                ... on DynamicMultipleChoiceQuestion {
                  hintText
                  options {
                    edges {
                      node {
                        slug
                        label
                      }
                    }
                  }
                }
                ... on DynamicChoiceQuestion {
                  hintText
                  options {
                    edges {
                      node {
                        slug
                        label
                      }
                    }
                  }
                }
                ... on FormQuestion {
                  subForm {
                    slug
                  }
                }
                ... on StaticQuestion {
                  staticContent
                }
                ... on CalculatedFloatQuestion {
                  hintText
                  calcExpression
                }
                ... on FilesQuestion {
                  hintText
                }
              }
            }
          }
        }
    """

    result = schema_executor(
        query,
        variable_values={
            "search": str(question.label),
            "forms": [extract_global_id_input_fields(form)["id"]],
        },
    )

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("question__meta", [{"meta": "set"}])
def test_copy_question(db, question, question_option_factory, schema_executor):
    def sorted_option_list(q):
        return sorted(
            list(
                models.QuestionOption.objects.filter(question=q).values_list(
                    "option", flat=True
                )
            )
        )

    question_option_factory.create_batch(5, question=question)
    query = """
        mutation CopyQuestion($input: CopyQuestionInput!) {
          copyQuestion(input: $input) {
            question {
              slug
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": {
            "source": question.pk,
            "slug": "new-question",
            "label": "Test Question",
        }
    }
    result = schema_executor(query, variable_values=inp)

    assert not result.errors

    question_slug = result.data["copyQuestion"]["question"]["slug"]
    assert question_slug == "new-question"
    new_question = models.Question.objects.get(pk=question_slug)
    assert new_question.label == "Test Question"
    assert new_question.meta == question.meta
    assert new_question.type == question.type
    assert new_question.configuration == question.configuration
    assert new_question.row_form == question.row_form
    assert new_question.is_hidden == question.is_hidden
    assert new_question.is_required == question.is_required
    assert new_question.source == question
    assert sorted_option_list(new_question) == sorted_option_list(question)


@pytest.mark.parametrize(
    "mutation",
    [
        "SaveTextQuestion",
        "SaveTextareaQuestion",
        "SaveIntegerQuestion",
        "SaveFloatQuestion",
        "SaveDateQuestion",
        "SaveFilesQuestion",
        "SaveCalculatedFloatQuestion",
    ],
)
@pytest.mark.parametrize(
    "question__is_required,success", (("true", True), ("true|invalid", False))
)
def test_save_question(db, snapshot, question, mutation, schema_executor, success):
    mutation_func = mutation[0].lower() + mutation[1:]
    query = f"""
        mutation {mutation}($input: {mutation}Input!) {{
          {mutation_func}(input: $input) {{
            question {{
              id
              slug
              label
              meta
              __typename
            }}
            clientMutationId
          }}
        }}
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveQuestionSerializer, question
        )
    }
    result = schema_executor(query, variable_values=inp)

    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "question__type,question__configuration,question__format_validators,answer__value,success",
    [
        (models.Question.TYPE_TEXT, {"max_length": 10}, [], "foo", True),
        (models.Question.TYPE_TEXT, {"max_length": 10}, ["email"], "foo", True),
        (
            models.Question.TYPE_TEXT,
            {"max_length": 10},
            ["notavalidator"],
            "foo",
            False,
        ),
    ],
)
def test_save_text_question(db, question, schema_executor, answer, success):
    query = """
        mutation SaveTextQuestion($input: SaveTextQuestionInput!) {
          saveTextQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on TextQuestion {
                maxLength
                hintText
                formatValidators {
                  edges {
                    node {
                      slug
                      name
                      regex
                      errorMsg
                    }
                  }
                }
                defaultAnswer {
                  value
                }
              }
            }
            clientMutationId
          }
        }
    """

    question.default_answer = answer
    question.hint_text = "test"
    question.save()

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveTextQuestionSerializer, question
        )
    }
    result = schema_executor(query, variable_values=inp)
    assert not bool(result.errors) == success
    if success:
        assert result.data["saveTextQuestion"]["question"]["maxLength"] == 10
        if question.format_validators:
            assert (
                result.data["saveTextQuestion"]["question"]["formatValidators"][
                    "edges"
                ][0]["node"]["slug"]
                == "email"
            )
        assert (
            result.data["saveTextQuestion"]["question"]["defaultAnswer"]["value"]
            == "foo"
        )
        assert result.data["saveTextQuestion"]["question"]["hintText"] == "test"


@pytest.mark.parametrize(
    "question__type,question__configuration,answer__value",
    [(models.Question.TYPE_TEXTAREA, {"max_length": 10}, "foo")],
)
def test_save_textarea_question(db, question, answer, schema_executor):
    query = """
        mutation SaveTextareaQuestion($input: SaveTextareaQuestionInput!) {
          saveTextareaQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on TextareaQuestion {
                maxLength
                hintText
                defaultAnswer {
                  value
                }
              }
            }
            clientMutationId
          }
        }
    """

    question.default_answer = answer
    question.hint_text = "test"
    question.save()

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveTextareaQuestionSerializer, question
        )
    }
    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    assert result.data["saveTextareaQuestion"]["question"]["maxLength"] == 10
    assert (
        result.data["saveTextareaQuestion"]["question"]["defaultAnswer"]["value"]
        == "foo"
    )
    assert result.data["saveTextareaQuestion"]["question"]["hintText"] == "test"


@pytest.mark.parametrize(
    "question__type,question__configuration,answer__value,success",
    [
        (models.Question.TYPE_FLOAT, {"max_value": 10.0, "min_value": 0.0}, 0.3, True),
        (models.Question.TYPE_FLOAT, {"max_value": 1.0, "min_value": 10.0}, 0.3, False),
        (models.Question.TYPE_FLOAT, {"step": 1.0}, 0.3, True),
        (models.Question.TYPE_FLOAT, {"step": -0.01}, 0.3, False),
    ],
)
def test_save_float_question(db, snapshot, question, schema_executor, answer, success):
    query = """
        mutation SaveFloatQuestion($input: SaveFloatQuestionInput!) {
          saveFloatQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on FloatQuestion {
                minValue
                maxValue
                hintText
                defaultAnswer {
                  value
                }
              }
            }
            clientMutationId
          }
        }
    """

    question.default_answer = answer
    question.hint_text = "test"
    question.save()

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveFloatQuestionSerializer, question
        )
    }
    result = schema_executor(query, variable_values=inp)
    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)
        assert (
            result.data["saveFloatQuestion"]["question"]["defaultAnswer"]["value"]
            == 0.3
        )
        assert result.data["saveFloatQuestion"]["question"]["hintText"] == "test"


@pytest.mark.parametrize(
    "question__type,question__configuration,answer__value,success",
    [
        (models.Question.TYPE_INTEGER, {"max_value": 10, "min_value": 0}, 23, True),
        (models.Question.TYPE_INTEGER, {"max_value": 1, "min_value": 10}, 23, False),
    ],
)
def test_save_integer_question(
    db, snapshot, question, answer, success, schema_executor
):
    query = """
        mutation SaveIntegerQuestion($input: SaveIntegerQuestionInput!) {
          saveIntegerQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on IntegerQuestion {
                minValue
                maxValue
                hintText
                defaultAnswer {
                  value
                }
              }
            }
            clientMutationId
          }
        }
    """

    question.default_answer = answer
    question.hint_text = "test"
    question.save()

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveIntegerQuestionSerializer, question
        )
    }
    result = schema_executor(query, variable_values=inp)
    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)
        assert (
            result.data["saveIntegerQuestion"]["question"]["defaultAnswer"]["value"]
            == 23
        )
        assert result.data["saveIntegerQuestion"]["question"]["hintText"] == "test"


@pytest.mark.parametrize("question__type", [models.Question.TYPE_MULTIPLE_CHOICE])
def test_save_multiple_choice_question(
    db, snapshot, question, question_option_factory, answer_factory, schema_executor
):
    question_option_factory.create_batch(2, question=question)

    option_ids = question.options.order_by("-slug").values_list("slug", flat=True)

    question.default_answer = answer_factory(value=list(option_ids), question=question)
    question.hint_text = "test"
    question.save()

    query = """
        mutation SaveMultipleChoiceQuestion($input: SaveMultipleChoiceQuestionInput!) {
          saveMultipleChoiceQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on MultipleChoiceQuestion {
                options {
                  edges {
                    node {
                      slug
                      label
                    }
                  }
                }
                hintText
                defaultAnswer {
                  value
                }
              }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveMultipleChoiceQuestionSerializer, question
        )
    }
    inp["input"]["options"] = option_ids
    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("with_default", [True, False])
@pytest.mark.parametrize("question__type", [models.Question.TYPE_CHOICE])
def test_save_choice_question(
    db,
    snapshot,
    question,
    question_option,
    answer_factory,
    schema_executor,
    with_default,
):
    query = """
        mutation SaveChoiceQuestion($input: SaveChoiceQuestionInput!) {
          saveChoiceQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on ChoiceQuestion {
                options {
                  edges {
                    node {
                      slug
                      label
                    }
                  }
                }
                hintText
                defaultAnswer {
                  value
                }
              }
            }
            clientMutationId
          }
        }
    """

    if with_default:
        question.default_answer = answer_factory(
            value=question_option.option.slug, question=question
        )
        question.hint_text = "test"
        question.save()

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveChoiceQuestionSerializer, question
        )
    }
    if not with_default:
        question.delete()
    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("delete", [True, False])
@pytest.mark.parametrize(
    "question__type",
    [models.Question.TYPE_DYNAMIC_CHOICE, models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE],
)
def test_save_dynamic_choice_question(
    db, snapshot, question, delete, schema_executor, data_source_settings
):
    query = """
        mutation SaveDynamicChoiceQuestion($input: SaveDynamicChoiceQuestionInput!) {
          saveDynamicChoiceQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on DynamicChoiceQuestion {
                hintText
                options {
                  edges {
                    node {
                      slug
                      label
                    }
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    question.hint_text = "test"
    question.save()

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveDynamicChoiceQuestionSerializer, question
        )
    }
    if delete:
        question.delete()  # test creation
    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("delete", [True, False])
@pytest.mark.parametrize(
    "question__type", [models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE]
)
def test_save_dynamic_multiple_choice_question(
    db,
    snapshot,
    question,
    delete,
    question_option_factory,
    schema_executor,
    data_source_settings,
):
    query = """
        mutation SaveDynamicMultipleChoiceQuestion($input: SaveDynamicMultipleChoiceQuestionInput!) {
          saveDynamicMultipleChoiceQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on DynamicMultipleChoiceQuestion {
                hintText
                options {
                  edges {
                    node {
                      slug
                      label
                    }
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    question.hint_text = "test"
    question.save()

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveDynamicMultipleChoiceQuestionSerializer, question
        )
    }
    if delete:
        question.delete()  # test creation
    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("question__type", [models.Question.TYPE_TABLE])
def test_save_table_question(db, snapshot, question, schema_executor):
    query = """
        mutation SaveTableQuestion($input: SaveTableQuestionInput!) {
          saveTableQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on TableQuestion {
                rowForm {
                  slug
                }
                hintText
              }
            }
            clientMutationId
          }
        }
    """
    question.hint_text = "test"
    question.save()

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveTableQuestionSerializer, question
        )
    }
    question.delete()  # test creation
    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("question__type", [models.Question.TYPE_FORM])
def test_save_form_question(db, snapshot, question, question_option, schema_executor):
    query = """
        mutation SaveFormQuestion($input: SaveFormQuestionInput!) {
          saveFormQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on FormQuestion {
                subForm {
                  slug
                }
              }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveFormQuestionSerializer, question
        )
    }
    question.delete()  # test creation
    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("question__type", [models.Question.TYPE_STATIC])
def test_save_static_question(db, snapshot, question, schema_executor):
    query = """
        mutation SaveStaticQuestion($input: SaveStaticQuestionInput!) {
          saveStaticQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on StaticQuestion {
                staticContent
              }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveStaticQuestionSerializer, question
        )
    }
    result = schema_executor(query, variable_values=inp)
    assert not bool(result.errors)
    snapshot.assert_match(result.data)


def test_all_questions_slug_filter(
    db,
    schema_executor,
    question_option_factory,
    question_factory,
    form_factory,
    form_question_factory,
    option_factory,
):
    query = """
        query FilteredQuestions {
          allQuestions {
            edges {
              node {
                slug
              }
            }
          }
        }
    """
    questions = question_factory.create_batch(4)

    forms = form_factory.create_batch(2)

    for question in questions:
        for form in forms:
            question.forms.through.objects.create(form=form, question=question)

    num_questions = models.Question.objects.all().count()
    result = schema_executor(query)

    assert not result.errors
    assert len(result.data["allQuestions"]["edges"]) == num_questions


def test_calc_dependents(db, question_factory):
    dep1, dep2, dep3 = question_factory.create_batch(3)

    assert not any([dep1.calc_dependents, dep2.calc_dependents, dep3.calc_dependents])

    calc_q = question_factory(
        type=models.Question.TYPE_CALCULATED_FLOAT,
        calc_expression=f"['{dep1.slug}'|answer, '{dep2.slug}'|answer]|sum",
    )
    other_calc_q = question_factory(
        type=models.Question.TYPE_CALCULATED_FLOAT,
        calc_expression=f"'{dep1.slug}'|answer + '{dep2.slug}'|answer * '{dep3.slug}'|answer",
    )
    dep1.refresh_from_db()
    dep2.refresh_from_db()
    dep3.refresh_from_db()

    def slug_in_deps(slug, deps):
        return [slug in dependents for dependents in [q.calc_dependents for q in deps]]

    assert all(slug_in_deps(calc_q.slug, [dep1, dep2]))
    assert all(slug_in_deps(other_calc_q.slug, [dep1, dep2, dep3]))

    calc_q.calc_expression = f"'{dep2.slug}'|answer + '{dep3.slug}'|answer"
    calc_q.save()
    dep1.refresh_from_db()
    dep2.refresh_from_db()
    dep3.refresh_from_db()

    assert dep1.calc_dependents == [other_calc_q.slug]
    assert all(slug_in_deps(calc_q.slug, [dep2, dep3]))
    assert all(slug_in_deps(other_calc_q.slug, [dep1, dep2, dep3]))

    calc_q.delete()

    dep1.refresh_from_db()
    dep2.refresh_from_db()
    dep3.refresh_from_db()
    assert not any(slug_in_deps(calc_q.slug, [dep1, dep2, dep3]))
    assert all(slug_in_deps(other_calc_q.slug, [dep1, dep2, dep3]))


@pytest.mark.parametrize("question__slug", ["dep-question"])
@pytest.mark.parametrize(
    "question__type,answer_value,calc_expression,expected",
    [
        (models.Question.TYPE_FLOAT, 1.5, "'dep-question'|answer * 3", 4.5),
        (models.Question.TYPE_FLOAT, 0, "'dep-question'|answer * 3", 0),
        (models.Question.TYPE_INTEGER, 100, "'dep-question'|answer", 100.0),
        (models.Question.TYPE_INTEGER, 100, "'dep-question'|answer / 10 * 99", 990.0),
    ],
)
def test_calculated_question(
    db,
    schema_executor,
    form_question,
    question_factory,
    answer_value,
    calc_expression,
    expected,
):
    form = form_question.form
    question = form_question.question

    question_factory(
        slug="not_in_form",
        type=models.Question.TYPE_CALCULATED_FLOAT,
        calc_expression=f"'{question.slug}'|answer",
    )

    query = """
        mutation SaveCalculatedQuestion($input: SaveCalculatedFloatQuestionInput!) {
          saveCalculatedFloatQuestion (input: $input) {
            question {
              slug
             __typename
             ... on CalculatedFloatQuestion {
               calcExpression
               hintText
             }
            }
          }
        }
    """

    inp = {
        "input": {
            "slug": "calc-question",
            "label": "Calculated Float Question",
            "calcExpression": calc_expression,
            "hintText": "test",
        }
    }
    result = schema_executor(query, variable_values=inp)

    assert not result.errors
    assert result.data["saveCalculatedFloatQuestion"]["question"]["hintText"] == "test"

    question.refresh_from_db()
    assert set(question.calc_dependents) == set(["calc-question", "not_in_form"])

    calc_question = models.Question.objects.get(slug="calc-question")
    form.questions.add(calc_question)

    query = """
        mutation SaveDocument($input: SaveDocumentInput!) {
          saveDocument (input: $input) {
            document {
              id
              answers {
                edges {
                  node {
                    ... on FloatAnswer {
                      value
                    }
                  }
                }
              }
            }
          }
        }
    """

    inp = {"input": {"form": form.slug}}
    result = schema_executor(query, variable_values=inp)
    assert not result.errors

    calc_answer = calc_question.answers.first()
    assert calc_answer
    assert calc_answer.value is None

    q_type = question.type.capitalize()
    query = f"""
        mutation SaveDocument{q_type}Answer($input: SaveDocument{q_type}AnswerInput!) {{
          saveDocument{q_type}Answer (input: $input) {{
            answer {{
              id
            }}
          }}
        }}
    """

    inp = {
        "input": {
            "document": extract_global_id(
                result.data["saveDocument"]["document"]["id"]
            ),
            "question": question.slug,
            "value": answer_value,
        }
    }
    result = schema_executor(query, variable_values=inp)
    assert not result.errors

    calc_answer.refresh_from_db()
    assert calc_answer
    assert calc_answer.value == expected


@pytest.mark.parametrize(
    "expr,expected,calc_deps",
    [
        ("'sub_question'|answer", 100.0, ["sub_question"]),
        ("'table'|answer|mapby('column')[0]", 99.99, ["table", "column"]),
        ("'other'|answer", 3.0, ["other"]),
        (
            "'sub_question'|answer && 'table'|answer|mapby('column', 'column2') ? 'other'|answer: -1",
            3.0,
            ["sub_question", "table", "column", "column2", "other"],
        ),
    ],
)
def test_nested_calculated_question(
    db,
    schema_executor,
    form_and_document,
    form_question_factory,
    question_factory,
    expr,
    expected,
    calc_deps,
):
    form, document, questions, answers_dict = form_and_document(True, True)

    sub_question = questions["sub_question"]
    sub_question.type = models.Question.TYPE_INTEGER
    sub_question.save()
    sub_question_a = answers_dict["sub_question"]
    sub_question_a.value = 100
    sub_question_a.save()

    column_a = answers_dict["column"]
    column_a.value = 99.99
    column_a.save()

    questions["other"] = form_question_factory(
        form=form, question__slug="other", question__type=models.Question.TYPE_INTEGER
    ).question

    questions["column2"] = question_factory(
        slug="column2", is_required="false", is_hidden="false"
    )
    form_question_factory(
        form=questions["table"].row_form, question=questions["column2"]
    )

    api.save_answer(question=questions["other"], document=document, value=3)

    questions["calc"] = form_question_factory(
        form=form,
        question__slug="calc",
        question__type=models.Question.TYPE_CALCULATED_FLOAT,
        question__calc_expression=expr,
    )

    for dep in calc_deps:
        questions[dep].refresh_from_db()
        assert questions[dep].calc_dependents == ["calc"]


def test_recursive_calculated_question(
    db, schema_executor, form, form_question_factory, question_factory, document_factory
):
    base = question_factory(
        slug="base",
        type=models.Question.TYPE_INTEGER,
    )
    calc_1 = question_factory(
        slug="calc-1",
        type=models.Question.TYPE_CALCULATED_FLOAT,
        calc_expression='"base"|answer(0) + 1',
    )
    calc_2 = question_factory(
        slug="calc-2",
        type=models.Question.TYPE_CALCULATED_FLOAT,
        calc_expression='"calc-1"|answer(0) * 2',
    )
    form_question_factory(form=form, question=base)
    form_question_factory(form=form, question=calc_1)
    form_question_factory(form=form, question=calc_2)

    document = document_factory(form=form)
    query = """
        mutation saveDocumentIntegerAnswer($input: SaveDocumentIntegerAnswerInput!) {
          saveDocumentIntegerAnswer(input: $input) {
            clientMutationId
          }
        }
    """

    variables = {
        "input": {
            "document": to_global_id("Document", document.pk),
            "question": to_global_id("Question", base.pk),
            "value": 3,
        }
    }

    schema_executor(query, variable_values=variables)

    calc_ans = document.answers.get(question_id="calc-2")
    assert calc_ans.value == 8


def test_calculated_question_update_calc_expr(
    db, schema_executor, form_and_document, form_question_factory, mocker
):
    form, document, questions_dict, answers_dict = form_and_document(True, True)

    sub_question = questions_dict["sub_question"]
    sub_question.type = models.Question.TYPE_INTEGER
    sub_question.save()
    sub_question_a = answers_dict["sub_question"]
    sub_question_a.value = 100
    sub_question_a.save()

    calc_question = form_question_factory(
        form=form,
        question__slug="calc_question",
        question__type=models.Question.TYPE_CALCULATED_FLOAT,
        question__calc_expression="'sub_question'|answer + 1",
    ).question

    calc_ans = document.answers.get(question_id="calc_question")
    assert calc_ans.value == 101
    # spying on update_or_create_calc_answer doesn't seem to work, so we spy on
    # QuestionJexl.evaluate instead
    spy = mocker.spy(QuestionJexl, "evaluate")
    calc_question.calc_expression = "'sub_question'|answer -1"
    calc_question.save()
    assert spy.call_count > 0
    call_count = spy.call_count
    calc_ans.refresh_from_db()
    assert calc_ans.value == 99

    calc_question.label = "New Label"
    calc_question.save()
    # if the calc expression is not changed, no jexl evaluation should be done
    assert spy.call_count == call_count


def test_recalc_missing_dependency(
    db, schema_executor, form_and_document, form_question_factory, mocker
):
    """
    Test recalculation behaviour for missing dependency.

    Verify the update mechanism works correctly even if a calc dependency
    does not exist in a given form.
    """
    form, document, questions_dict, answers_dict = form_and_document(True, True)

    sub_question = questions_dict["sub_question"]
    sub_question.type = models.Question.TYPE_INTEGER
    sub_question.save()

    spy = mocker.spy(domain_logic.SaveAnswerLogic, "recalculate_dependents")

    # Calculated question in another form
    form_question_factory(
        # in another form entirely
        question__slug="some_calc_question",
        question__type=models.Question.TYPE_CALCULATED_FLOAT,
        question__calc_expression="'sub_question'|answer + 1",
    ).question

    # update answer - should trigger recalc
    api.save_answer(sub_question, document, value=100)

    assert spy.call_count > 0


def test_calculated_question_answer_document(
    db,
    schema_executor,
    form_and_document,
    form_question_factory,
    answer_factory,
    document_factory,
):
    form, document, questions_dict, answers_dict = form_and_document(True, True)

    table = questions_dict["table"]
    table_a = answers_dict["table"]
    row_form = table.row_form
    column = questions_dict["column"]
    column.type = models.Question.TYPE_INTEGER
    column.save()

    column_a1 = column.answers.get()
    column_a1.value = 100
    column_a1.save()

    form_question_factory(
        form=form,
        question__slug="calc_question",
        question__type=models.Question.TYPE_CALCULATED_FLOAT,
        question__calc_expression="'table'|answer|mapby('column')[0] + 'table'|answer|mapby('column')[1]",
    ).question

    # adding another row will make make the expression valid
    row_doc = document_factory(form=row_form, family=document)
    column_a2 = answer_factory(document=row_doc, question_id=column.slug, value=200)

    api.save_answer(
        question=table,
        document=document,
        documents=list(table_a.documents.all()) + [row_doc],
    )

    calc_ans = document.answers.get(question_id="calc_question")
    assert calc_ans.value == 300

    api.save_answer(
        question=column_a2.question,
        document=row_doc,
        value=100,
    )
    calc_ans.refresh_from_db()
    column.refresh_from_db()
    assert column.calc_dependents == ["calc_question"]
    assert calc_ans.value == 200

    # removing the row will make it invalid again
    table_a.documents.remove(row_doc)
    api.save_answer(
        question=table,
        document=document,
        documents=[table_a.documents.first()],
    )
    calc_ans.refresh_from_db()
    assert calc_ans.value is None


@pytest.mark.parametrize("question__type", [models.Question.TYPE_ACTION_BUTTON])
def test_save_action_button_question(db, snapshot, question, schema_executor):
    query = """
        mutation SaveActionButtonQuestion($input: SaveActionButtonQuestionInput!) {
          saveActionButtonQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on ActionButtonQuestion {
                action
                color
                validateOnEnter
              }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveActionButtonQuestionSerializer, question
        )
    }
    result = schema_executor(query, variable_values=inp)
    assert not bool(result.errors)
    snapshot.assert_match(result.data)


def test_init_of_calc_questions_queries(
    db,
    form,
    form_and_document,
    form_question_factory,
    django_assert_num_queries,
):
    (form, document, questions_dict, _) = form_and_document(
        use_table=True, use_subform=True, table_row_count=10
    )

    form_question_factory(
        form=form,
        question__slug="calc_question",
        question__type=models.Question.TYPE_CALCULATED_FLOAT,
        question__calc_expression="'table'|answer|mapby('column')|sum + 'top_question'|answer + 'sub_question'|answer",
    )

    with django_assert_num_queries(31):
        api.save_answer(questions_dict["top_question"], document, value="1")
