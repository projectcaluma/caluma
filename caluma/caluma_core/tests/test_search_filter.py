def test_search_in_filter_collection(db, schema_executor, form_factory):
    form_factory(name="Test 1")
    form_factory(name="Test 2")
    form_factory(name="Test 3")

    query = """
        query($search: String!) {
          allForms(filter: [{ search: $search }]) {
            edges {
              node {
                slug
                name
              }
            }
          }
        }
    """

    result = schema_executor(query, variable_values={"search": "Test 2"})
    assert not result.errors

    assert len(result.data["allForms"]["edges"]) == 1
    assert result.data["allForms"]["edges"][0]["node"]["name"] == "Test 2"
