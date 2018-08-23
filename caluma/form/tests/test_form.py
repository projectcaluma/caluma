from ...schema import schema
from ...tests import extract_global_id_input_fields, extract_serializer_input_fields
from ..serializers import FormSerializer


def test_save_form(db, snapshot, form):
    query = """
        mutation SaveForm($input: SaveFormInput!) {
          saveForm(input: $input) {
            form {
              id
              slug
              name
              meta
            }
            clientMutationId
          }
        }
    """

    inp = {"input": extract_serializer_input_fields(FormSerializer, form)}
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


def test_archive_form(db, form):
    query = """
        mutation ArchiveForm($input: ArchiveFormInput!) {
          archiveForm(input: $input) {
            form {
              isArchived
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query, variables={"input": extract_global_id_input_fields(form)}
    )

    assert not result.errors
    assert result.data["archiveForm"]["form"]["isArchived"]

    form.refresh_from_db()
    assert form.is_archived


def test_publish_form(db, form):
    query = """
        mutation PublishForm($input: PublishFormInput!) {
          publishForm(input: $input) {
            form {
              isPublished
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query, variables={"input": extract_global_id_input_fields(form)}
    )

    assert not result.errors
    assert result.data["publishForm"]["form"]["isPublished"]

    form.refresh_from_db()
    assert form.is_published
