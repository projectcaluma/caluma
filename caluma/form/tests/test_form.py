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
    inp["input"].pop("meta")
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)
