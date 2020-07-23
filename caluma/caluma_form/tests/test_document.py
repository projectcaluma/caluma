import pytest
from graphql_relay import to_global_id

from ...caluma_core.relay import extract_global_id
from ...caluma_core.tests import extract_serializer_input_fields
from ...caluma_core.visibilities import BaseVisibility, filter_queryset_for
from ...caluma_form.models import Answer, Document, Question
from ...caluma_form.schema import Document as DocumentNodeType
from .. import serializers


@pytest.mark.parametrize(
    "question__type,question__data_source,answer__value,answer__date",
    [
        (Question.TYPE_INTEGER, None, 1, None),
        (Question.TYPE_FLOAT, None, 2.1, None),
        (Question.TYPE_TEXT, None, "somevalue", None),
        (Question.TYPE_MULTIPLE_CHOICE, None, ["somevalue", "anothervalue"], None),
        (Question.TYPE_TABLE, None, None, None),
        (Question.TYPE_DATE, None, None, "2019-02-22"),
        (Question.TYPE_FILE, None, "some-file.pdf", None),
        (Question.TYPE_FILE, None, "some-other-file.pdf", None),
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
          allDocuments(search: $search) {
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
                      ... on FileAnswer {
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

    search = isinstance(answer.value, list) and " ".join(answer.value) or answer.value

    if question.type == Question.TYPE_FILE:
        if answer.value == "some-other-file.pdf":
            settings.MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = False
            minio_mock.bucket_exists.return_value = False
        # we need to set the pk here in order to match the snapshots
        answer.file = file_factory(
            name=answer.value, pk="09c697fb-fd0a-4345-bb9c-99df350b0cdb"
        )
        answer.value = None
        answer.save()
        search = answer.file.name

    result = schema_executor(query, variable_values={"search": search})
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
    file_question = question_factory(type=Question.TYPE_FILE)
    form_question_factory(question=file_question, form=form)
    answer_factory(
        question=file_question, value=None, document=document, file=file_factory()
    )

    form_question = question_factory(type=Question.TYPE_FORM)
    form_question_factory(question=form_question, form=form)

    table_question = question_factory(type=Question.TYPE_TABLE)
    form_question_factory(question=table_question, form=form)

    query = """
        query ($id: ID!) {
          allDocuments(id: $id) {
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
          ... on FileAnswer {
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

    with django_assert_num_queries(8):
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
                answers(question: $question) {
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
                answers(questions: $questions) {
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


@pytest.mark.parametrize("update", [True, False])
def test_save_document(db, document, schema_executor, update):
    query = """
        mutation SaveDocument($input: SaveDocumentInput!) {
          saveDocument(input: $input) {
            document {
                form {
                  slug
                }
                id
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.DocumentSerializer, document
        )
    }

    if not update:
        # not update = create = we don't pass the ID
        del inp["input"]["id"]

    result = schema_executor(query, variable_values=inp)

    assert not result.errors
    assert result.data["saveDocument"]["document"]["form"]["slug"] == document.form.slug

    same_id = extract_global_id(result.data["saveDocument"]["document"]["id"]) == str(
        document.id
    )

    # if updating, the resulting document must be the same
    assert same_id == update


@pytest.mark.parametrize("delete_answer", [True, False])
@pytest.mark.parametrize("option__slug", ["option-slug"])
@pytest.mark.parametrize(
    "question__type,question__configuration,question__data_source,question__format_validators,answer__value,answer__date,mutation,success",
    [
        (
            Question.TYPE_INTEGER,
            {},
            None,
            [],
            1,
            None,
            "SaveDocumentIntegerAnswer",
            True,
        ),
        (
            Question.TYPE_INTEGER,
            {"min_value": 100},
            None,
            [],
            1,
            None,
            "SaveDocumentIntegerAnswer",
            False,
        ),
        (Question.TYPE_FLOAT, {}, None, [], 2.1, None, "SaveDocumentFloatAnswer", True),
        (
            Question.TYPE_FLOAT,
            {"min_value": 100.0},
            None,
            [],
            1,
            None,
            "SaveDocumentFloatAnswer",
            False,
        ),
        (
            Question.TYPE_TEXT,
            {},
            None,
            [],
            "Test",
            None,
            "SaveDocumentStringAnswer",
            True,
        ),
        (
            Question.TYPE_TEXT,
            {"max_length": 1},
            None,
            [],
            "toolong",
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_DATE,
            {},
            None,
            [],
            None,
            "1900-01-01",
            "SaveDocumentDateAnswer",
            False,
        ),
        (
            Question.TYPE_DATE,
            {},
            None,
            [],
            None,
            "2019-02-22",
            "SaveDocumentDateAnswer",
            True,
        ),
        (Question.TYPE_FILE, {}, None, [], None, None, "SaveDocumentFileAnswer", False),
        (
            Question.TYPE_FILE,
            {},
            None,
            [],
            "some-file.pdf",
            None,
            "SaveDocumentFileAnswer",
            True,
        ),
        (
            Question.TYPE_FILE,
            {},
            None,
            [],
            "not-exist.pdf",
            None,
            "SaveDocumentFileAnswer",
            True,
        ),
        (
            Question.TYPE_TEXT,
            {"min_length": 10},
            None,
            [],
            "tooshort",
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_TABLE,
            {},
            None,
            [],
            None,
            None,
            "SaveDocumentTableAnswer",
            True,
        ),
        (
            Question.TYPE_TEXTAREA,
            {},
            None,
            [],
            "Test",
            None,
            "SaveDocumentStringAnswer",
            True,
        ),
        (
            Question.TYPE_TEXTAREA,
            {"max_length": 1},
            None,
            [],
            "toolong",
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_MULTIPLE_CHOICE,
            {},
            None,
            [],
            ["option-slug"],
            None,
            "SaveDocumentListAnswer",
            True,
        ),
        (
            Question.TYPE_MULTIPLE_CHOICE,
            {},
            None,
            [],
            ["option-slug", "option-invalid-slug"],
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_CHOICE,
            {},
            None,
            [],
            "option-slug",
            None,
            "SaveDocumentStringAnswer",
            True,
        ),
        (
            Question.TYPE_CHOICE,
            {},
            None,
            [],
            "invalid-option-slug",
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            {},
            "MyDataSource",
            [],
            ["5.5", "1"],
            None,
            "SaveDocumentListAnswer",
            True,
        ),
        (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            {},
            "MyDataSource",
            [],
            ["not in data"],
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_DYNAMIC_CHOICE,
            {},
            "MyDataSource",
            [],
            "5.5",
            None,
            "SaveDocumentStringAnswer",
            True,
        ),
        (
            Question.TYPE_DYNAMIC_CHOICE,
            {},
            "MyDataSource",
            [],
            "not in data",
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_TEXT,
            {},
            None,
            ["email"],
            "some text",
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_TEXT,
            {},
            None,
            ["email"],
            "test@example.com",
            None,
            "SaveDocumentStringAnswer",
            True,
        ),
        (
            Question.TYPE_TEXTAREA,
            {},
            None,
            ["email"],
            "some text",
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_TEXTAREA,
            {},
            None,
            ["email"],
            "test@example.com",
            None,
            "SaveDocumentStringAnswer",
            True,
        ),
    ],
)
def test_save_document_answer(
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
):
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
              ... on FileAnswer {{
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

    if question.type == Question.TYPE_FILE:
        if answer.value == "some-file.pdf":
            minio_mock.bucket_exists.return_value = False
        answer.value = None
        answer.save()

    if question.type == Question.TYPE_DATE:
        inp["input"]["value"] = answer.date
        answer.value = None
        answer.save()
        # Date format is enforced in the model. So we initially had to use a valid date
        # here we're able to change it:
        if answer.date == "1900-01-01":
            inp["input"]["value"] = "not a date"

    if delete_answer:
        # delete answer to force create test instead of update
        Answer.objects.filter(pk=answer.pk).delete()

    result = schema_executor(query, variable_values=inp)

    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)


@pytest.mark.parametrize("delete_answer", [True, False])
@pytest.mark.parametrize(
    "question__type,question__is_required,answer__value",
    [(Question.TYPE_TEXT, "false", None)],
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
    question,
    form_factory,
    question_factory,
):
    """Ensure that we can save incomplete row documents."""
    question.row_form = form_factory()
    question.save()

    question.row_form.questions.add(question_factory(is_required="true"))

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
    inp["input"]["value"] = [
        str(document.pk) for document in document_factory.create_batch(1)
    ]
    result = schema_executor(query, variable_values=inp)
    assert result.errors


@pytest.mark.parametrize("question__type", [Question.TYPE_TABLE])
def test_save_document_table_answer_setting_family(
    db,
    schema_executor,
    answer,
    answer_factory,
    document_factory,
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
    inp["input"]["value"] = {remaining_document.pk, to_be_deleted_document.pk}
    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    assert {main_pk, to_be_deleted_table_row.pk} | inp["input"]["value"] == set(
        Document.objects.filter(family=main_family).values_list("id", flat=True)
    ), "family is not set to main document"
    to_be_deleted_document.refresh_from_db()
    assert to_be_deleted_document.family == main_family
    to_be_deleted_table_row.refresh_from_db()
    assert to_be_deleted_table_row.family == main_family

    # detach one document answer from table answer
    inp["input"]["value"] = {remaining_document.pk}
    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    assert {main_pk} | inp["input"]["value"] == set(
        Document.objects.filter(family=main_family).values_list("id", flat=True)
    )
    to_be_deleted_document.refresh_from_db()
    assert to_be_deleted_document.family == to_be_deleted_document
    to_be_deleted_table_row.refresh_from_db()
    assert to_be_deleted_table_row.family == to_be_deleted_document.family


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


@pytest.mark.parametrize(
    "question__is_required,question__type,question__data_source,is_valid",
    [
        ("true", Question.TYPE_TEXT, None, False),
        ("false", Question.TYPE_TEXT, None, True),
        ("true", Question.TYPE_TEXT, None, True),
    ],
)
def test_validity_query(db, form, question, document, is_valid, schema_executor):

    form.questions.through.objects.create(form=form, question=question, sort=1)
    document.form = form
    document.save()

    if is_valid:
        document.answers.create(question=question, value="hello")
    else:
        assert not document.answers.exists()

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

    result = schema_executor(query, variable_values={"document_id": document.id})

    # if is_valid, we expect 0 errors, otherwise one
    num_errors = int(not is_valid)

    assert result.data["documentValidity"]["edges"][0]["node"]["id"] == str(document.id)
    assert result.data["documentValidity"]["edges"][0]["node"]["isValid"] == is_valid
    assert (
        len(result.data["documentValidity"]["edges"][0]["node"]["errors"]) == num_errors
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

    result = schema_executor(query, variable_values={"document_id": document.id})

    if hide_documents:
        assert result.data["documentValidity"] is None
    else:
        assert len(result.data["documentValidity"]["edges"]) == 1


def test_remove_document_without_case(db, document, answer, schema_executor):
    query = """
        mutation RemoveDocument($input: RemoveDocumentInput!) {
          removeDocument(input: $input) {
            document {
              id
            }
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
            document {
              id
            }
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
            document {
              id
            }
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
    question_factory,
    form_factory,
    form_question_factory,
    schema_executor,
    minio_mock,
):
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
        form=main_form, question__type=Question.TYPE_FILE
    )

    # main_document
    #   - table_answer
    #       - row_document_1
    #           - sub_question answer:"foo"
    #   - other_question answer:"something"
    #   - file_question answer: b"a file"

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
    assert new_file_answer.file.name == file_answer.file.name
    assert new_file_answer.file.object_name != file_answer.file.object_name

    # table docs and answers are moved
    new_table_answer = new_document.answers.get(question=table_question)
    assert new_table_answer.documents.count() == 1

    result_table_answer_document = new_table_answer.documents.first()
    assert result_table_answer_document.source == row_document_1
    assert result_table_answer_document.family == new_document
    assert set(ans.value for ans in result_table_answer_document.answers.all()) == set(
        ans.value for ans in row_document_1.answers.all()
    )
