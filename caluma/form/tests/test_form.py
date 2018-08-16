from ...schema import schema


def test_all_forms_connection(db, form, snapshot):
    query = """
    query AllFormsQuery {
      allForms {
        edges {
          node {
            id
            slug
            name
            description
            meta
          }
        }
      }
    }
    """

    result = schema.execute(query)
    assert not result.errors
    snapshot.assert_match(result.data)
