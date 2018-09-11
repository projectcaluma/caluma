from ...schema import schema


def test_query_all_task_specifications(db, snapshot, task_specification):
    query = """
        query AllTaskSpecifications($name: String!) {
          allTaskSpecifications(name: $name) {
            edges {
              node {
                type
                slug
                name
                description
                meta
              }
            }
          }
        }
    """

    result = schema.execute(query, variables={"name": task_specification.name})

    assert not result.errors
    snapshot.assert_match(result.data)
