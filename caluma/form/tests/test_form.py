import pytest
from graphql_relay import to_global_id

from .. import models
from ...schema import schema
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

    inp = {"input": FormSerializer(form).data}
    inp["input"]["meta"] = "{}"
    inp["input"]["clientMutationId"] = "testid"
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


def test_delete_form(db, snapshot, form):
    query = """
        mutation DeleteForm($input: DeleteFormInput!) {
          deleteForm(input: $input) {
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

    global_id = to_global_id(models.Form.__name__, form.pk)
    result = schema.execute(
        query, variables={"input": {"id": global_id, "clientMutationId": "testid"}}
    )

    assert not result.errors
    snapshot.assert_match(result.data)

    with pytest.raises(models.Form.DoesNotExist):
        form.refresh_from_db()
