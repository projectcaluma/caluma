import json

import pytest
from django.utils.dateparse import parse_date
from graphql.error import GraphQLError
from graphql_relay import to_global_id
from rest_framework.exceptions import ValidationError

from caluma.caluma_data_source.tests.data_sources import MyDataSourceWithOnCopy

from ...caluma_core.relay import extract_global_id
from ...caluma_core.tests import extract_serializer_input_fields
from ...caluma_core.visibilities import BaseVisibility, filter_queryset_for
from ...caluma_form.models import Answer, Document, DynamicOption, Question
from ...caluma_form.schema import Document as DocumentNodeType
from .. import api, serializers


@pytest.mark.parametrize(
    "question__type,question__data_source,answer__value,answer__date",
    [
        (Question.TYPE_INTEGER, None, 1, None),
        (Question.TYPE_FLOAT, None, 2.1, None),
        (Question.TYPE_TEXT, None, "somevalue", None),
        (Question.TYPE_MULTIPLE_CHOICE, None, ["somevalue", "anothervalue"], None),
        (Question.TYPE_TABLE, None, None, None),
        (Question.TYPE_DATE, None, None, "2019-02-22"),
        (Question.TYPE_FILES, None, [{"name": "some-file.pdf"}], None),
        (Question.TYPE_FILES, None, [{"name": "some-other-file.pdf"}], None),
        (Question.TYPE_DYNAMIC_CHOICE, "MyDataSource", "5.5", None),
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, "MyDataSource", ["5.5"], None),
    ],
)
def test_query_all_documents(
    db,
    snapshot,
    form_question,
    form,
    document,
    document_factory,
    question_factory,
    form_question_factory,
    answer_factory,
    file_factory,
    answer_document,
    answer,
    schema_executor,
    question,
    minio_mock,
    data_source_settings,
    settings,
):
    query = """
        query AllDocumentsQuery($search: String) {
          allDocuments(filter: [{search: $search}]) {
            totalCount
            edges {
              node {
                createdByUser
                answers {
                  totalCount
                  edges {
                    node {
                      __typename
                      question {
                        slug
                        label
                      }
                      ... on StringAnswer {
                        string_value: value
                      }
                      ... on IntegerAnswer {
                        integer_value: value
                      }
                      ... on ListAnswer {
                        list_value: value
                      }
                      ... on FloatAnswer {
                        float_value: value
                      }
                      ... on DateAnswer {
                        date_value: value
                      }
                      ... on TableAnswer {
                        table_value: value {
                          form {
                            slug
                          }
                        }
                      }
                      ... on FilesAnswer {
                        fileValue: value {
                          name
                          downloadUrl
                          metadata
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """

    def _value(val):
        # Extract searchable value from given input if it exists
        ret = {
            list: lambda: _value(val[0]),
            dict: lambda: _value(list(val.keys())[0]),
        }
        return ret.get(type(val), lambda: val)()

    search = _value(answer.value)

    if question.type == Question.TYPE_FILES:
        if answer.value[0]["name"] == "some-other-file.pdf":
            settings.MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = False
            minio_mock.bucket_exists.return_value = False
        # we need to set the pk here in order to match the snapshots
        answer.files.set(
            [
                file_factory(
                    name=answer.value,
                    pk="09c697fb-fd0a-4345-bb9c-99df350b0cdb",
                    answer=answer,
                )
            ]
        )
        answer.value = None
        answer.save()
        search = answer.files.get().name

    result = schema_executor(query, variable_values={"search": str(search)})
    assert not result.errors
    snapshot.assert_match(result.data)


def test_complex_document_query_performance(
    db,
    schema_executor,
    document,
    form,
    form_question_factory,
    question_factory,
    answer_factory,
    file_factory,
    question_option_factory,
    django_assert_num_queries,
    minio_mock,
):
    answers = answer_factory.create_batch(5, document=document)
    for answer in answers:
        form_question_factory(question=answer.question, form=form)
    multiple_choice_question = question_factory(type=Question.TYPE_MULTIPLE_CHOICE)
    form_question_factory(question=multiple_choice_question, form=form)
    question_option_factory.create_batch(10, question=multiple_choice_question)
    answer_factory(question=multiple_choice_question)
    file_question = question_factory(type=Question.TYPE_FILES)
    form_question_factory(question=file_question, form=form)
    answer_factory(
        question=file_question, value=None, document=document, files=[file_factory()]
    )

    form_question = question_factory(type=Question.TYPE_FORM)
    form_question_factory(question=form_question, form=form)

    table_question = question_factory(type=Question.TYPE_TABLE)
    form_question_factory(question=table_question, form=form)

    query = """
        query ($id: ID!) {
          allDocuments(filter: [{id: $id}]) {
            edges {
              node {
                ...FormDocument
              }
            }
          }
        }

        fragment FormDocument on Document {
          id
          answers {
            edges {
              node {
                ...FieldAnswer
              }
            }
          }
          form {
            slug
            questions {
              edges {
                node {
                  ...FieldQuestion
                }
              }
            }
          }
        }

        fragment FieldAnswer on Answer {
          id
          __typename
          question {
            slug
          }
          ... on StringAnswer {
            stringValue: value
          }
          ... on IntegerAnswer {
            integerValue: value
          }
          ... on FloatAnswer {
            floatValue: value
          }
          ... on DateAnswer {
            dateValue: value
          }
          ... on ListAnswer {
            listValue: value
          }
          ... on FilesAnswer {
            fileValue: value {
              name
              downloadUrl
              metadata
            }
          }
        }

        fragment FieldQuestion on Question {
          slug
          label
          isRequired
          isHidden
          ... on TextQuestion {
            textMaxLength: maxLength
          }
          ... on TextareaQuestion {
            textareaMaxLength: maxLength
          }
          ... on IntegerQuestion {
            integerMinValue: minValue
            integerMaxValue: maxValue
          }
          ... on FloatQuestion {
            floatMinValue: minValue
            floatMaxValue: maxValue
          }
          ... on ChoiceQuestion {
            choiceOptions: options {
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
              name
            }
          }
          ... on TableQuestion {
            rowForm {
              slug
            }
          }
          ... on MultipleChoiceQuestion {
            multipleChoiceOptions: options {
              edges {
                node {
                  slug
                  label
                }
              }
            }
          }
        }
    """

    with django_assert_num_queries(10):
        result = schema_executor(query, variable_values={"id": str(document.pk)})
    assert not result.errors


def test_query_all_documents_filter_answers_by_question(
    db, document, answer, question, answer_factory, schema_executor
):
    answer_factory(document=document)

    query = """
        query AllDocumentsQuery($question: ID!) {
          allDocuments {
            edges {
              node {
                answers(filter: [{question: $question}]) {
                  edges {
                    node {
                      id
                    }
                  }
                }
              }
            }
          }
        }
    """

    result = schema_executor(query, variable_values={"question": question.slug})
    assert not result.errors
    assert len(result.data["allDocuments"]["edges"]) == 1
    result_document = result.data["allDocuments"]["edges"][0]["node"]
    assert len(result_document["answers"]["edges"]) == 1
    result_answer = result_document["answers"]["edges"][0]["node"]
    assert extract_global_id(result_answer["id"]) == str(answer.id)


def test_query_all_documents_filter_answers_by_questions(
    db, document_factory, question_factory, answer_factory, schema_executor
):
    documents = []
    answers = []
    questions = []

    for _ in range(3):
        documents.append(document_factory())
        questions.append(question_factory())
        answers.append(answer_factory(document=documents[-1], question=questions[-1]))

    query = """
        query AllDocumentsQuery($questions: [ID!]) {
          allDocuments {
            edges {
              node {
                id
                answers(filter: [{questions: $questions}]) {
                  edges {
                    node {
                      id
                    }
                  }
                }
              }
            }
          }
        }
    """

    result = schema_executor(
        query, variable_values={"questions": [questions[0].slug, questions[1].slug]}
    )
    assert not result.errors
    assert len(result.data["allDocuments"]["edges"]) == 3

    result_lengths = [
        (extract_global_id(doc["node"]["id"]), len(doc["node"]["answers"]["edges"]))
        for doc in result.data["allDocuments"]["edges"]
    ]
    expect_data = [(str(documents[idx].pk), int(idx < 2)) for idx in range(3)]
    assert set(expect_data) == set(result_lengths)


SAVE_DOCUMENT_QUERY = """
    mutation SaveDocument($input: SaveDocumentInput!) {
      saveDocument(input: $input) {
        document {
          form {
            slug
          }
          id
          answers {
            edges {
              node {
                ... on StringAnswer {
                  strValue: value
                }
                ... on IntegerAnswer {
                  intValue: value
                }
                ... on FloatAnswer {
                  floatValue: value
                }
              }
            }
          }
        }
        clientMutationId
      }
    }
"""


def _setup_for_save_document(form_question_factory, answer_factory, form_factory, form):
    """Set up form structure for the save_document test cases.

    Just to avoid copy/pasta or a complicated multiplex test.

    Use the given `form` and add some structure to it:

    * `some_int` - Integer
    * (random slug) - calculated float on basis of above question
    * subform (random slug)
        - sub form question (random slug) - Text with default answer
    """
    # create an integer question that has a default answer
    form_question_int = form_question_factory(
        question__type=Question.TYPE_INTEGER,
        form=form,
        question__slug="some_int",
    )
    default_answer = answer_factory(
        question=form_question_int.question, value=23, document=None
    )
    form_question_int.question.default_answer = default_answer
    form_question_int.question.save()

    # create a calculated question referencing the integer question we created above
    form_question_factory(
        question__type=Question.TYPE_CALCULATED_FLOAT,
        form=form,
        question__calc_expression=f"'{form_question_int.question.slug}'|answer * 2",
    )

    # create a sub-form with a question with a default_answer
    sub_form = form_factory()
    form_question_factory(
        question__type=Question.TYPE_FORM,
        form=form,
        question__sub_form=sub_form,
    )
    sub_form_question = form_question_factory(
        question__type=Question.TYPE_TEXT, form=sub_form
    )
    sub_default_answer = answer_factory(
        question=sub_form_question.question, value="foo"
    )
    sub_form_question.question.default_answer = sub_default_answer
    sub_form_question.question.save()


@pytest.mark.parametrize("update", [True, False])
def test_save_document_client(
    db,
    document,
    schema_executor,
    form_factory,
    form_question_factory,
    answer_factory,
    update,
):
    """Test saving of a document via GQL client.

    We test two variants - either an Update, or a Create operation.
    The test form contains two questions with a default answer, as well as
    a calculated question.

    In the Create operation, we assume that the default answers are copied into
    the new document, and then the calculated question is, well, calculated and
    is added as an answer to the document as well, leading to three answers on the
    document.

    In the Update operation, the form is actually created after the document,
    and so during the form construction (see `_setup_for_save_document()`), when
    the calculated question is attached to the form, it's being run, creating
    an (empty) answer. But changing (or adding) default answers shall not
    update existing documents, and thus the resulting number of answers in this
    operation is just the one (calc) answer.
    """
    _setup_for_save_document(
        form_question_factory, answer_factory, form_factory, document.form
    )
    default_answer = document.form.questions.get(slug="some_int").default_answer
    inp = {
        "input": extract_serializer_input_fields(
            serializers.DocumentSerializer, document
        )
    }
    if not update:
        # not update = create = we don't pass the ID
        del inp["input"]["id"]

    result = schema_executor(SAVE_DOCUMENT_QUERY, variable_values=inp)

    assert not result.errors
    assert result.data["saveDocument"]["document"]["form"]["slug"] == document.form.slug

    same_id = extract_global_id(result.data["saveDocument"]["document"]["id"]) == str(
        document.id
    )

    # if updating, the resulting document must be the same
    assert same_id == update

    # 1 in update is the calc question's answer, but the questions with default
    # answers don't get their answers auto-created. 3 is a new document,
    # therefore the default answers get copied into the document
    assert len(result.data["saveDocument"]["document"]["answers"]["edges"]) == (
        1 if update else 3
    )
    if not update:
        assert sorted(
            [
                str(a["node"]["intValue"])
                if "intValue" in a["node"]
                else (
                    a["node"]["strValue"]
                    if "strValue" in a["node"]
                    else str(a["node"]["floatValue"])
                )
                for a in result.data["saveDocument"]["document"]["answers"]["edges"]
            ]
        ) == ["23", "46.0", "foo"]

    # Make sure the default answers document is still None
    default_answer.refresh_from_db()
    assert default_answer.document_id is None


@pytest.mark.parametrize("update", [True, False])
def test_save_document_python(
    db,
    document,
    schema_executor,
    form_factory,
    form_question_factory,
    answer_factory,
    update,
):
    """Test saving a document via the Python API.

    For detailed explanation about the expected behaviour, see the docs for
    `test_save_document_client()`.
    """
    _setup_for_save_document(
        form_question_factory, answer_factory, form_factory, document.form
    )
    default_answer = document.form.questions.get(slug="some_int").default_answer

    doc = (
        api.save_document(document.form, document=document)
        if update
        else api.save_document(document.form)
    )
    assert (doc.pk == document.pk) == update

    assert doc.answers.count() == (1 if update else 3)
    if not update:
        assert sorted([str(a.value) for a in doc.answers.iterator()]) == [
            "23",
            "46",
            "foo",
        ]

    # Make sure the default answers document is still None
    default_answer.refresh_from_db()
    assert default_answer.document_id is None


@pytest.mark.parametrize("use_python_api", [True, False])  # noqa:C901
@pytest.mark.parametrize("delete_answer", [True, False])
@pytest.mark.parametrize("option__slug", ["option-slug"])
@pytest.mark.parametrize(
    "question__type,question__configuration,question__data_source,question__format_validators,answer__value,answer__date,mutation,success",
    [
        (Question.TYPE_INTEGER, {}, None, [], 1, None, "SaveDocumentIntegerAnswer", True),
        (Question.TYPE_INTEGER, {"min_value": 100}, None, [], 1, None, "SaveDocumentIntegerAnswer", False),
        (Question.TYPE_FLOAT, {}, None, [], 2.1, None, "SaveDocumentFloatAnswer", True),
        (Question.TYPE_FLOAT, {"min_value": 100.0}, None, [], 1, None, "SaveDocumentFloatAnswer", False),
        (Question.TYPE_TEXT, {}, None, [], "Test", None, "SaveDocumentStringAnswer", True),
        (Question.TYPE_TEXT, {"max_length": 1}, None, [], "toolong", None, "SaveDocumentStringAnswer", False),
        (Question.TYPE_DATE, {}, None, [], None, "1900-01-01", "SaveDocumentDateAnswer", False),
        (Question.TYPE_DATE, {}, None, [], None, "2019-02-22", "SaveDocumentDateAnswer", True),
        (Question.TYPE_FILES, {}, None, [], None, None, "SaveDocumentFilesAnswer", False),
        (Question.TYPE_FILES, {}, None, [], [{"name": "some-file.pdf"}], None, "SaveDocumentFilesAnswer", True),
        (Question.TYPE_FILES, {}, None, [], [{"name": "not-exist.pdf"}], None, "SaveDocumentFilesAnswer", True),
        (Question.TYPE_TEXT, {"min_length": 10}, None, [], "tooshort", None, "SaveDocumentStringAnswer", False),
        (Question.TYPE_TABLE, {}, None, [], None, None, "SaveDocumentTableAnswer", True),
        (Question.TYPE_TEXTAREA, {}, None, [], "Test", None, "SaveDocumentStringAnswer", True),
        (Question.TYPE_TEXTAREA, {"max_length": 1}, None, [], "toolong", None, "SaveDocumentStringAnswer", False),
        (Question.TYPE_MULTIPLE_CHOICE, {}, None, [], ["option-slug"], None, "SaveDocumentListAnswer", True),
        (Question.TYPE_MULTIPLE_CHOICE, {}, None, [], ["option-slug", "option-invalid-slug"], None, "SaveDocumentStringAnswer", False),
        (Question.TYPE_CHOICE, {}, None, [], "option-slug", None, "SaveDocumentStringAnswer", True),
        (Question.TYPE_CHOICE, {}, None, [], "invalid-option-slug", None, "SaveDocumentStringAnswer", False),
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, {}, "MyDataSource", [], ["5.5", "1"], None, "SaveDocumentListAnswer", True),
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, {}, "MyDataSource", [], ["not in data"], None, "SaveDocumentStringAnswer", False),
        (Question.TYPE_DYNAMIC_CHOICE, {}, "MyDataSource", [], "5.5", None, "SaveDocumentStringAnswer", True),
        (Question.TYPE_DYNAMIC_CHOICE, {}, "MyDataSource", [], "not in data", None, "SaveDocumentStringAnswer", False),
        (Question.TYPE_TEXT, {}, None, ["email"], "some text", None, "SaveDocumentStringAnswer", False),
        (Question.TYPE_TEXT, {}, None, ["email"], "test@example.com", None, "SaveDocumentStringAnswer", True),
        (Question.TYPE_TEXTAREA, {}, None, ["email"], "some text", None, "SaveDocumentStringAnswer", False),
        (Question.TYPE_TEXTAREA, {}, None, ["email"], "test@example.com", None, "SaveDocumentStringAnswer", True),
    ],
)  # fmt:skip
def test_save_document_answer(  # noqa:C901
    db,
    snapshot,
    question,
    answer,
    mutation,
    question_option,
    document_factory,
    answer_factory,
    answer_document_factory,
    question_factory,
    file_factory,
    success,
    schema_executor,
    delete_answer,
    minio_mock,
    data_source_settings,
    use_python_api,
    admin_user,
):
    # question needs to be part of our form
    answer.document.form.questions.add(question, through_defaults={"sort": 3})

    mutation_func = mutation[0].lower() + mutation[1:]
    query = f"""
        mutation {mutation}($input: {mutation}Input!) {{
          {mutation_func}(input: $input) {{
            answer {{
              __typename
              ... on StringAnswer {{
                stringValue: value
              }}
              ... on IntegerAnswer {{
                integerValue: value
              }}
              ... on ListAnswer {{
                listValue: value
              }}
              ... on FloatAnswer {{
                floatValue: value
              }}
              ... on ListAnswer {{
                listValue: value
              }}
              ... on DateAnswer {{
                dateValue: value
              }}
              ... on TableAnswer {{
                table_value: value {{
                  form {{
                    slug
                  }}
                }}
              }}
              ... on FilesAnswer {{
                fileValue: value {{
                  name
                  uploadUrl
                }}
              }}
            }}
            clientMutationId
          }}
        }}
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveAnswerSerializer, answer
        )
    }

    if question.type == Question.TYPE_TABLE:
        documents = document_factory.create_batch(2, form=question.row_form)
        # create a subtree
        sub_question = question_factory(type=Question.TYPE_TEXT)
        document_answer = answer_factory(question=sub_question)
        documents[0].answers.add(document_answer)
        answer_document_factory(answer=answer, document=documents[0])

        inp["input"]["value"] = [str(document.pk) for document in documents]

    if question.type == Question.TYPE_FILES:
        if answer.value:
            file_name = answer.value[0]["name"]
            if file_name == "some-file.pdf":
                minio_mock.bucket_exists.return_value = False
            answer.value = None
            answer.files.all().delete()
            inp["input"]["value"] = [{"name": file_name}]

            answer.save()

    if question.type == Question.TYPE_DATE:
        inp["input"]["value"] = answer.date
        answer.value = None
        answer.save()
        # Date format is enforced in the model. So we initially had to use a valid date
        # here we're able to change it:
        if answer.date == "1900-01-01":
            inp["input"]["value"] = "not a date"

        if use_python_api and success:
            inp["input"]["value"] = parse_date(inp["input"]["value"])

    if delete_answer:
        # delete answer to force create test instead of update
        Answer.objects.filter(pk=answer.pk).delete()

    if not use_python_api:
        result = schema_executor(query, variable_values=inp)

        assert not bool(result.errors) == success

        if success:
            snapshot.assert_match(result.data)
    else:
        if success:
            answer = api.save_answer(
                question, answer.document, user=admin_user, value=inp["input"]["value"]
            )
            snapshot.assert_match(answer)
        else:
            with pytest.raises((ValidationError, GraphQLError)):
                api.save_answer(
                    question,
                    answer.document,
                    user=admin_user,
                    value=inp["input"]["value"],
                )


@pytest.mark.parametrize("delete_answer", [True, False])
@pytest.mark.parametrize(
    "question__type,question__is_required,answer__value",
    [(Question.TYPE_TEXT, "false", "old value that needs to be deleted")],
)
def test_save_document_answer_empty(
    db, snapshot, question, answer, schema_executor, delete_answer
):
    query = """
        mutation saveDocumentStringAnswer($input: SaveDocumentStringAnswerInput!) {
          saveDocumentStringAnswer(input: $input) {
            answer {
              __typename
              ... on StringAnswer {
                stringValue: value
              }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": {
            "document": to_global_id("StringAnswer", answer.document.pk),
            "question": to_global_id("StringAnswer", answer.question.pk),
        }
    }

    if delete_answer:
        # delete answer to force create test instead of update
        Answer.objects.filter(pk=answer.pk).delete()

    result = schema_executor(query, variable_values=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("question__type", [Question.TYPE_TABLE])
def test_save_document_table_answer_invalid_row_document(
    db,
    schema_executor,
    answer,
    document_factory,
    form_question_factory,
    question,
    form_factory,
    question_factory,
):
    """Ensure that we can save incomplete row documents."""
    question.row_form = form_factory()
    question.save()
    # question needs to be part of our form
    form_question_factory(
        form=question.row_form, question=question_factory(is_required="true")
    )
    form_question_factory(form=answer.document.form, question=question)

    query = """
        mutation SaveDocumentTableAnswer($input: SaveDocumentTableAnswerInput!) {
            saveDocumentTableAnswer(input: $input) {
                clientMutationId
            }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveAnswerSerializer, answer
        )
    }
    inp["input"]["value"] = [str(document_factory(form=question.row_form).pk)]

    result = schema_executor(query, variable_values=inp)
    assert not result.errors


@pytest.mark.parametrize("question__type", [Question.TYPE_TABLE])
def test_save_document_table_answer_invalid_row_form(
    db, schema_executor, answer, document_factory
):
    """Test validation that row documents must have correct row type."""
    query = """
        mutation SaveDocumentTableAnswer($input: SaveDocumentTableAnswerInput!) {
            saveDocumentTableAnswer(input: $input) {
                clientMutationId
            }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveAnswerSerializer, answer
        )
    }
    inp["input"]["value"] = [str(document_factory().pk)]

    result = schema_executor(query, variable_values=inp)
    assert result.errors


@pytest.mark.parametrize("question__type", [Question.TYPE_TABLE])
def test_save_document_table_answer_setting_family(
    db,
    schema_executor,
    answer,
    answer_factory,
    document_factory,
    form_question_factory,
    answer_document_factory,
):
    query = """
        mutation SaveDocumentTableAnswer($input: SaveDocumentTableAnswerInput!) {
            saveDocumentTableAnswer(input: $input) {
                clientMutationId
            }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveAnswerSerializer, answer
        )
    }

    form_question_factory(form=answer.document.form, question=answer.question)

    main_pk = answer.document.pk
    main_family = answer.document.family
    remaining_document = document_factory(form=answer.question.row_form)
    to_be_deleted_document = document_factory(form=answer.question.row_form)
    answer_factory(document=to_be_deleted_document)
    to_be_deleted_table_row = document_factory(
        form=answer.question.row_form, family=to_be_deleted_document.family
    )
    table_answer = answer_factory(
        question=answer.question, document=to_be_deleted_document
    )
    answer_document_factory(answer=table_answer, document=to_be_deleted_table_row)

    # attach documents to table answer
    inp["input"]["value"] = {str(remaining_document.pk), str(to_be_deleted_document.pk)}
    result = schema_executor(query, variable_values=inp)

    def assert_pk_set(expected, actual, assert_msg=None):
        assert set(str(x) for x in expected) == set(str(x) for x in actual)

    assert not result.errors

    assert_pk_set(
        [main_pk, to_be_deleted_table_row.pk] + list(inp["input"]["value"]),
        Document.objects.filter(family=main_family).values_list("id", flat=True),
        "family is not set to main document",
    )

    to_be_deleted_document.refresh_from_db()
    assert to_be_deleted_document.family == main_family
    to_be_deleted_table_row.refresh_from_db()
    assert to_be_deleted_table_row.family == main_family

    # detach one document answer from table answer
    inp["input"]["value"] = {str(remaining_document.pk)}
    result = schema_executor(query, variable_values=inp)
    assert not result.errors

    assert_pk_set(
        [main_pk] + list(inp["input"]["value"]),
        Document.objects.filter(family=main_family).values_list("id", flat=True),
    )

    to_be_deleted_document.refresh_from_db()
    assert to_be_deleted_document.family == to_be_deleted_document
    to_be_deleted_table_row.refresh_from_db()
    assert to_be_deleted_table_row.family == to_be_deleted_document.family


@pytest.mark.parametrize("default_on_table", [True, False])
def test_save_document_table_answer_default_answer(
    db, form_and_document, answer_factory, default_on_table
):
    form, document, questions_dict, answers_dict = form_and_document(use_table=True)

    table_question = questions_dict["table"]
    row_question = questions_dict["column"]

    row_question_default_answer = answer_factory(question=row_question, value=23)
    row_question.default_answer = row_question_default_answer
    row_question.save()

    table_answer = document.answers.filter(question__type=Question.TYPE_TABLE).first()

    if not default_on_table:
        table_answer.documents.first().answers.first().delete()

    table_question.default_answer = table_answer
    table_question.save()

    assert Document.objects.filter(form=form).count() == 1

    doc = api.save_document(document.form)

    assert Document.objects.filter(form=form).count() == 2

    assert doc.answers.count() == 1
    if default_on_table:
        assert (
            doc.answers.first().documents.first().answers.first().value
            == answers_dict["column"].value
        )
    else:
        assert doc.answers.first().documents.first().answers.first() is None


@pytest.mark.parametrize("answer__value", [1.1])
def test_query_answer_node(db, answer, schema_executor):
    global_id = to_global_id("FloatAnswer", answer.pk)

    node_query = """
    query AnswerNode($id: ID!) {
      node(id: $id) {
        ... on FloatAnswer {
            value
        }
      }
    }
    """

    result = schema_executor(node_query, variable_values={"id": global_id})
    assert not result.errors


@pytest.mark.parametrize("value,is_valid", [(None, False), ("Test", True)])
def test_validity_query(
    db,
    document,
    form_question_factory,
    form,
    is_valid,
    schema_executor,
    settings,
    value,
):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyDataSource"
    ]

    text_question = form_question_factory(
        form=form,
        question__type=Question.TYPE_TEXT,
        question__data_source=None,
        question__is_required="true",
    ).question

    dynamic_question = form_question_factory(
        form=form,
        question__type=Question.TYPE_DYNAMIC_CHOICE,
        question__data_source="MyDataSource",
        question__is_required="true",
    ).question

    document.form = form
    document.save()

    document.answers.create(question=text_question, value=value)
    document.answers.create(question=dynamic_question, value="something")

    query = """
        query($id: ID!) {
          documentValidity(id: $id) {
            edges {
              node {
                id
                isValid
                errors {
                  slug
                  errorMsg
                }
              }
            }
          }
        }
    """

    result = schema_executor(query, variable_values={"id": str(document.id)})

    # if is_valid, we expect 0 errors, otherwise one
    num_errors = int(not is_valid)

    assert result.data["documentValidity"]["edges"][0]["node"]["id"] == str(document.id)
    assert result.data["documentValidity"]["edges"][0]["node"]["isValid"] == is_valid
    assert (
        len(result.data["documentValidity"]["edges"][0]["node"]["errors"]) == num_errors
    )


@pytest.mark.parametrize("question__data_source", ["MyDataSourceWithContext"])
@pytest.mark.parametrize(
    "question__type,answer__value,context",
    [
        (
            Question.TYPE_DYNAMIC_CHOICE,
            "option-with-context",
            {"foo": "bar"},
        ),
        (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            ["option-with-context"],
            {"foo": "bar"},
        ),
    ],
)
def test_validity_query_with_context(
    db,
    document,
    form_question,
    schema_executor,
    settings,
    answer,
    context,
    question,
):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyDataSourceWithContext"
    ]

    answer.document = document
    answer.save()

    query = """
        query($id: ID!, $dataSourceContext: JSONString) {
          documentValidity(id: $id, dataSourceContext: $dataSourceContext) {
            edges {
              node {
                id
                isValid
                errors {
                  slug
                  errorMsg
                }
              }
            }
          }
        }
    """
    result = schema_executor(
        query,
        variable_values={
            "id": str(document.id),
            "dataSourceContext": json.dumps(context),
        },
    )

    assert result.data["documentValidity"]["edges"][0]["node"]["id"] == str(document.id)
    assert result.data["documentValidity"]["edges"][0]["node"]["isValid"] is True
    assert (
        bool(len(result.data["documentValidity"]["edges"][0]["node"]["errors"]))
        is False
    )


@pytest.mark.parametrize("hide_documents", [True, False])
def test_validity_with_visibility(
    db, form, document, schema_executor, hide_documents, mocker
):
    query = """
        query ValidateBaugesuch ($document_id: ID!) {
          documentValidity(
            id: $document_id
          ) {
            edges {
              node {
                id
                isValid
                errors {
                  slug
                  errorMsg
                }
              }
            }
          }
        }
    """

    class CustomVisibility(BaseVisibility):
        @filter_queryset_for(DocumentNodeType)
        def filter_queryset_for_document(self, node, queryset, info):
            if hide_documents:
                return queryset.none()
            return queryset

    mocker.patch("caluma.caluma_core.types.Node.visibility_classes", [CustomVisibility])

    result = schema_executor(query, variable_values={"document_id": str(document.id)})

    if hide_documents:
        assert result.data["documentValidity"] is None
    else:
        assert len(result.data["documentValidity"]["edges"]) == 1


def test_remove_document_without_case(db, document, answer, schema_executor):
    query = """
        mutation RemoveDocument($input: RemoveDocumentInput!) {
          removeDocument(input: $input) {
            clientMutationId
          }
        }
    """

    result = schema_executor(
        query, variable_values={"input": {"document": str(document.pk)}}
    )

    assert not result.errors
    with pytest.raises(Document.DoesNotExist):
        Document.objects.get(pk=document.pk)
    with pytest.raises(Answer.DoesNotExist):
        Answer.objects.get(pk=answer.pk)


def test_remove_document_with_case(db, document, answer, case, schema_executor):
    query = """
        mutation RemoveDocument($input: RemoveDocumentInput!) {
          removeDocument(input: $input) {
            clientMutationId
          }
        }
    """

    result = schema_executor(
        query, variable_values={"input": {"document": str(document.pk)}}
    )

    assert result.errors
    Document.objects.get(pk=document.pk)
    Answer.objects.get(pk=answer.pk)


def test_remove_document_without_case_table(
    db,
    document_factory,
    answer_factory,
    answer_document_factory,
    question_factory,
    form_question_factory,
    schema_executor,
):
    question = question_factory(type=Question.TYPE_TABLE)
    documents = document_factory.create_batch(2, form=question.row_form)

    sub_question = question_factory(type=Question.TYPE_TEXT)
    form_question_factory(form=question.row_form, question=sub_question)

    sub_answers = answer_factory.create_batch(2, question=sub_question)
    documents[0].answers.add(sub_answers[0])
    documents[1].answers.add(sub_answers[1])

    table_answer = answer_factory(question=question)
    answer_document_factory(answer=table_answer, document=documents[0])
    answer_document_factory(answer=table_answer, document=documents[1])

    query = """
        mutation RemoveDocument($input: RemoveDocumentInput!) {
          removeDocument(input: $input) {
            clientMutationId
          }
        }
    """

    result = schema_executor(
        query, variable_values={"input": {"document": str(table_answer.document.pk)}}
    )

    assert not result.errors
    for document in [table_answer.document, *documents]:
        with pytest.raises(Document.DoesNotExist):
            Document.objects.get(pk=document.pk)
    for answer in [table_answer, *sub_answers]:
        with pytest.raises(Answer.DoesNotExist):
            Answer.objects.get(pk=answer.pk)


def test_copy_document(
    db,
    document_factory,
    answer_factory,
    answer_document_factory,
    dynamic_option_factory,
    question_factory,
    form_factory,
    form_question_factory,
    schema_executor,
    minio_mock,
    settings,
):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyDataSource",
    ]

    main_form = form_factory(slug="main-form")
    table_question = question_factory(
        type=Question.TYPE_TABLE, slug="table-question", row_form=form_factory()
    )
    form_question_factory(form=main_form, question=table_question)

    sub_question = form_question_factory(
        form=table_question.row_form,
        question__type=Question.TYPE_TEXT,
        question__slug="sub_question",
    )
    other_question = form_question_factory(
        form=main_form,
        question__type=Question.TYPE_TEXT,
        question__slug="other_question",
    )
    file_question = form_question_factory(
        form=main_form, question__type=Question.TYPE_FILES
    )
    dynamic_choice_question = form_question_factory(
        form=main_form, question__type=Question.TYPE_DYNAMIC_CHOICE
    )
    dynamic_multiple_choice_question = form_question_factory(
        form=main_form, question__type=Question.TYPE_DYNAMIC_CHOICE
    )

    # main_document
    #   - table_answer
    #       - row_document_1
    #           - sub_question answer:"foo"
    #   - other_question answer:"something"
    #   - file_question answer: b"a file"
    #   - dynamic_choice_question answer: "foo"
    #   - dynamic_multiple_choice_question answer: ["bar", "baz"]

    main_document = document_factory(form=main_form)
    table_answer = answer_factory(
        document=main_document, question=table_question, value=None
    )

    row_document_1 = document_factory(form=table_question.row_form)
    answer_document_factory(document=row_document_1, answer=table_answer)

    answer_factory(question=sub_question.question, document=row_document_1, value="foo")
    other_question_ans = answer_factory(
        question=other_question.question, document=main_document, value="something"
    )
    file_answer = answer_factory(
        question=file_question.question, document=main_document
    )
    answer_factory(
        question=dynamic_choice_question.question, document=main_document, value="foo"
    )
    answer_factory(
        question=dynamic_multiple_choice_question.question,
        document=main_document,
        value=["bar", "baz"],
    )

    for question, value in [
        (dynamic_choice_question.question, "foo"),
        (dynamic_multiple_choice_question.question, "bar"),
        (dynamic_multiple_choice_question.question, "baz"),
    ]:
        dynamic_option_factory(question=question, document=main_document, slug=value)

    query = """
        mutation CopyDocument($input: CopyDocumentInput!) {
          copyDocument(input: $input) {
            document {
              id
            }
            clientMutationId
          }
        }
    """

    result = schema_executor(
        query, variable_values={"input": {"source": str(main_document.pk)}}
    )
    assert not result.errors

    result_document_id = extract_global_id(
        result.data["copyDocument"]["document"]["id"]
    )

    new_document = Document.objects.get(pk=result_document_id)
    # main document is copied
    assert new_document.source_id == main_document.pk
    assert new_document.family == new_document
    assert new_document.family != main_document.family

    # answers are copied
    assert other_question.question.slug in new_document.answers.all().values_list(
        "question__slug", flat=True
    )
    assert (
        new_document.answers.get(question__slug=other_question.question.slug).value
        == other_question_ans.value
    )
    assert file_question.question.slug in new_document.answers.all().values_list(
        "question__slug", flat=True
    )
    new_file_answer = new_document.answers.get(
        question__slug=file_question.question.slug
    )
    assert new_file_answer.value == file_answer.value
    # file is copied
    minio_mock.copy_object.assert_called()

    old_file = file_answer.files.first()
    new_file = new_file_answer.files.first()
    assert new_file.name == old_file.name
    assert new_file.object_name != old_file.object_name

    # dynamic options are copied
    for question in [
        dynamic_choice_question.question,
        dynamic_multiple_choice_question.question,
    ]:
        assert (
            DynamicOption.objects.filter(
                question=question, document=new_document
            ).count()
            == DynamicOption.objects.filter(
                question=question, document=main_document
            ).count()
        )

    # table docs and answers are moved
    new_table_answer = new_document.answers.get(question=table_question)
    assert new_table_answer.documents.count() == 1

    result_table_answer_document = new_table_answer.documents.first()
    assert result_table_answer_document.source == row_document_1
    assert result_table_answer_document.family == new_document
    assert set(ans.value for ans in result_table_answer_document.answers.all()) == set(
        ans.value for ans in row_document_1.answers.all()
    )


@pytest.mark.parametrize(
    "on_copy_result",
    ["discard", "change", "retain"],
)
def test_copy_document_datasource_on_copy(
    db,
    document_factory,
    answer_factory,
    dynamic_option_factory,
    form_factory,
    form_question_factory,
    schema_executor,
    settings,
    on_copy_result,
):
    """Test datasource on_copy behavior while copying a document.

    While using a form with a single, and a dynamic multiple choice question, we are
    testing the behavior of the datasource on_copy method when discarding, changing or
    retaining answer values.

    The single dynamic question answer is answered with the on_copy_result value.
    The multiple dynamic question answer is answered with the set: value1,
    on_copy_result and value3.

    Examples:
    - discard:
        The single question answer is set to None. The dynamic option is not copied
        The multiple question answer is set to value1 and value3. The middle dynamic
            option is not copied
    - change:
        The single question answer is changed and the dynamic option copy is changed
        The multiple question answer's middle value is changed and the middle dynamic
            option copy is changed
    - retain:
        The single question answer is unchanged, the dynamic option is copied unchanged
        The multiple question answer is unchanged and the dynamic options are copied
            unchanged

    """
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyDataSourceWithOnCopy",
    ]

    # extract testing datasource values
    data_source = MyDataSourceWithOnCopy()
    allowed_values = data_source.get_data()
    value1 = allowed_values[0][0]
    value2 = allowed_values[1][0]
    value3 = allowed_values[2][0]

    # use the middle value for testing retaining the value unchanged
    if on_copy_result == "retain":
        on_copy_result = value2

    # set up the main form with dynamic choice and multiple choice questions
    main_form = form_factory(slug="main-form")
    dynamic_choice_question = form_question_factory(
        form=main_form,
        question__type=Question.TYPE_DYNAMIC_CHOICE,
    )
    dynamic_choice_question.question.data_source = "MyDataSourceWithOnCopy"
    dynamic_choice_question.question.save()
    dynamic_multiple_choice_question = form_question_factory(
        form=main_form,
        question__type=Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
    )
    dynamic_multiple_choice_question.question.data_source = "MyDataSourceWithOnCopy"
    dynamic_multiple_choice_question.question.save()
    main_document = document_factory(form=main_form)

    # answer single choice with the on_copy_result
    answer_factory(
        question=dynamic_choice_question.question,
        document=main_document,
        value=str(on_copy_result),
    )

    # answer multiple choice with the set: value1, on_copy_result and value3
    answer_factory(
        question=dynamic_multiple_choice_question.question,
        document=main_document,
        value=[
            str(value1),
            str(on_copy_result),
            str(value3),
        ],
    )

    # generate the dynamic options accordingly
    for question, value in [
        (dynamic_choice_question.question, on_copy_result),
        (dynamic_multiple_choice_question.question, value1),
        (dynamic_multiple_choice_question.question, on_copy_result),
        (dynamic_multiple_choice_question.question, value3),
    ]:
        dynamic_option_factory(question=question, document=main_document, slug=value)

    old_option = DynamicOption.objects.filter(
        question=dynamic_choice_question.question, document=main_document
    ).first()
    old_multi_options = DynamicOption.objects.filter(
        question=dynamic_multiple_choice_question.question, document=main_document
    )

    query = """
        mutation CopyDocument($input: CopyDocumentInput!) {
          copyDocument(input: $input) {
            document {
              id
            }
            clientMutationId
          }
        }
    """

    result = schema_executor(
        query, variable_values={"input": {"source": str(main_document.pk)}}
    )
    assert not result.errors

    # fetch the test datasource values for comparing discard and change behavior.
    discard_value, _ = data_source.get_discard_value()
    changed_value, changed_label = data_source.get_change_value()

    # fetch the copied document
    result_document_id = extract_global_id(
        result.data["copyDocument"]["document"]["id"]
    )
    new_document = Document.objects.get(pk=result_document_id)

    # test option and answer result of the single dynamic option
    new_answer = new_document.answers.get(question=dynamic_choice_question.question)
    new_option = DynamicOption.objects.filter(
        question=dynamic_choice_question.question, document=new_document
    ).first()
    if on_copy_result == "discard":
        # discarded, so the dynamic option is not copied
        assert new_option is discard_value
        assert new_answer.value is discard_value
    elif on_copy_result == "change":
        # changed, so the dynamic option is copied but with a different slug and label
        new_option.slug = changed_value
        new_option.label = changed_label
        assert new_answer.value == new_option.slug
    else:
        # retained, so the dynamic option is copied unchanged
        assert old_option.slug == new_option.slug
        assert old_option.label == new_option.label
        assert new_answer.value == old_option.slug

    # test option and answer result of the multiple dynamic options
    new_multi_answer = new_document.answers.get(
        question=dynamic_multiple_choice_question.question
    )
    new_multi_options = DynamicOption.objects.filter(
        question=dynamic_multiple_choice_question.question,
        document=new_document,
    ).order_by("created_at")
    if on_copy_result == "discard":
        # discarded, so the middle dynamic option is not copied.
        assert old_multi_options.count() - 1 == new_multi_options.count()
        assert new_multi_answer.value == [
            str(value1),
            str(value3),
        ]
    elif on_copy_result == "change":
        # changed, so the dynamic option is copied but with a different slug and label
        assert old_multi_options.count() == new_multi_options.count()
        assert old_multi_options[0].slug == new_multi_options[0].slug
        assert old_multi_options[0].label == new_multi_options[0].label
        assert new_multi_options[1].slug == changed_value
        assert new_multi_options[1].label == changed_label
        assert old_multi_options[2].slug == new_multi_options[2].slug
        assert old_multi_options[2].label == new_multi_options[2].label
        assert new_multi_answer.value == [
            str(value1),
            str(changed_value),
            str(value3),
        ]
    else:
        # retained, so the dynamic options are copied unchanged
        assert old_multi_options.count() == new_multi_options.count()
        assert set(old_multi_options.values_list("slug", flat=True)) == set(
            new_multi_options.values_list("slug", flat=True)
        )
        assert set(map(str, old_multi_options.values_list("label", flat=True))) == set(
            map(str, new_multi_options.values_list("label", flat=True))
        )
        assert new_multi_answer.value == [
            str(value1),
            str(value2),
            str(value3),
        ]


def assert_props(doc, answer):
    assert doc.last_modified_answer == answer
    assert doc.modified_content_at == answer.modified_at
    assert doc.modified_content_by_user == answer.modified_by_user
    assert doc.modified_content_by_group == answer.modified_by_group


def test_document_modified_content_properties(
    db, form_and_document, answer_factory, admin_user, schema_executor
):
    form, document, questions_dict, answers_dict = form_and_document(
        use_table=True, use_subform=True
    )

    row_document = Document.objects.get(form_id=questions_dict["table"].row_form_id)
    column_a = answers_dict["column"]

    top_a = answers_dict["top_question"]
    api.save_answer(top_a.question, document, user=admin_user, value="new value")
    top_a.refresh_from_db()

    # root doc points to newest changed answer, row doc to column answer
    assert_props(document, top_a)
    assert_props(row_document, column_a)

    # cached property on document still points to top_a as intended
    api.save_answer(column_a.question, column_a.document, user=admin_user, value=111.11)
    column_a.refresh_from_db()

    assert_props(document, top_a)

    # refreshed instance is pointing to column_a
    del document.last_modified_answer
    assert_props(document, column_a)

    # row document too
    del row_document.last_modified_answer
    assert_props(row_document, column_a)

    # same works with graphql
    query = """
        mutation saveDocumentStringAnswer($input: SaveDocumentIntegerAnswerInput!) {
          saveDocumentIntegerAnswer(input: $input) {
            answer {
              ... on IntegerAnswer {
                integerValue: value
              }
            }
            clientMutationId
          }
        }
    """

    sub_a = answers_dict["sub_question"]

    variables = {
        "input": {
            "document": to_global_id("Document", sub_a.document.pk),
            "question": to_global_id("IntegerAnswer", sub_a.question.pk),
            "value": 23,
        }
    }

    result = schema_executor(query, variable_values=variables)
    assert not result.errors

    sub_a.refresh_from_db()
    assert sub_a.value == 23

    query = """
        query AllDocumentsQuery($id: ID) {
          allDocuments(filter: [{id: $id}]) {
            totalCount
            edges {
              node {
                createdByUser
                modifiedContentAt
                modifiedContentByUser
                modifiedContentByGroup
                answers {
                  totalCount
                }
              }
            }
          }
        }
    """

    result = schema_executor(query, variable_values={"id": str(document.pk)})
    assert not result.errors

    node = result.data["allDocuments"]["edges"][0]["node"]
    assert node["modifiedContentAt"] == sub_a.modified_at.isoformat()
    assert node["modifiedContentByUser"] == sub_a.modified_by_user
    assert node["modifiedContentByGroup"] == sub_a.modified_by_group


@pytest.mark.parametrize(
    "question__type,answer__value,expected_values",
    [
        (Question.TYPE_CHOICE, "somevalue", "somevalue"),
        (
            Question.TYPE_MULTIPLE_CHOICE,
            ["somevalue", "anothervalue"],
            set(["somevalue", "anothervalue"]),
        ),
        (Question.TYPE_MULTIPLE_CHOICE, [], set()),
        (Question.TYPE_DYNAMIC_CHOICE, "somevalue", "somevalue"),
        (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            ["somevalue", "anothervalue"],
            set(["somevalue", "anothervalue"]),
        ),
        (Question.TYPE_TEXT, "somevalue", None),
    ],
)
def test_selected_options(
    db,
    snapshot,
    document,
    answer,
    question_option_factory,
    dynamic_option_factory,
    schema_executor,
    question,
    form,
    form_question_factory,
    expected_values,
):
    query = """
        query node($id: ID!) {
          node(id: $id) {
            ... on StringAnswer {
              string_value: value
              selectedOption {
                slug
                label
              }
            }
            ... on ListAnswer {
              list_value: value
              selectedOptions {
                edges {
                  node {
                    slug
                    label
                  }
                }
              }
            }
          }
        }
    """

    answer_type = "StringAnswer"

    if question.type == Question.TYPE_CHOICE:
        question_option_factory(option__slug=answer.value, question=question)
    elif question.type == Question.TYPE_DYNAMIC_CHOICE:
        # should not be displayed
        dynamic_option_factory(
            slug=answer.value,
            question=form_question_factory(form=form).question,
            document=document,
        )
        # should be displayed
        dynamic_option_factory(slug=answer.value, question=question, document=document)

    elif question.type == Question.TYPE_MULTIPLE_CHOICE:
        answer_type = "ListAnswer"
        for slug in answer.value:
            question_option_factory(option__slug=slug, question=question)

    elif question.type == Question.TYPE_DYNAMIC_MULTIPLE_CHOICE:
        answer_type = "ListAnswer"
        for slug in answer.value:
            # should not be displayed
            dynamic_option_factory(
                slug=slug,
                question=form_question_factory(form=form).question,
                document=document,
            )
            # should be displayed
            dynamic_option_factory(slug=slug, question=question, document=document)

    # add some options that must NOT show up in response
    question_option_factory(question=question)
    dynamic_option_factory(question=question, document=document)
    dynamic_option_factory(
        question=form_question_factory(form=form).question, document=document
    )

    result = schema_executor(
        query, variable_values={"id": to_global_id(answer_type, answer)}
    )
    assert not result.errors
    snapshot.assert_match(result.data)

    if question.type == Question.TYPE_TEXT:
        return

    elif question.type in [Question.TYPE_CHOICE, Question.TYPE_DYNAMIC_CHOICE]:
        returned_value = result.data["node"]["selectedOption"]["slug"]
    else:
        returned_value = set(
            [e["node"]["slug"] for e in result.data["node"]["selectedOptions"]["edges"]]
        )

    assert returned_value == expected_values


def test_flat_answer_map(db, form_and_document):
    (_form, document, _questions_dict, answers_dict) = form_and_document(
        use_table=True, use_subform=True
    )

    flat_answer_map = document.flat_answer_map()

    assert flat_answer_map["top_question"] == answers_dict["top_question"].value
    assert flat_answer_map["sub_question"] == answers_dict["sub_question"].value
    assert flat_answer_map["table"] == [
        {"column": answers_dict["table"].documents.first().answers.first().value}
    ]


def test_efficient_init_of_calc_questions(
    db, schema_executor, form, form_question_factory, question_factory, mocker
):
    calc_1 = question_factory(
        slug="calc-1",
        type=Question.TYPE_CALCULATED_FLOAT,
        calc_expression="1",
    )
    calc_2 = question_factory(
        slug="calc-2",
        type=Question.TYPE_CALCULATED_FLOAT,
        calc_expression='"calc-1"|answer(0) * 2',
    )
    form_question_factory(form=form, question=calc_1)
    form_question_factory(form=form, question=calc_2)

    from caluma.caluma_form.jexl import QuestionJexl

    spy = mocker.spy(QuestionJexl, "evaluate")
    document = api.save_document(form)
    # twice for calc value, once for hidden state of calc-1
    assert spy.call_count == 2

    calc_ans = document.answers.get(question_id="calc-2")
    assert calc_ans.value == 2
