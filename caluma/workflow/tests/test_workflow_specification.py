from ...schema import schema


def test_query_all_workflow_specifications(db, snapshot, workflow_specification, flow):
    query = """
        query AllWorkflowSpecifications($name: String!) {
          allWorkflowSpecifications(name: $name) {
            edges {
              node {
                slug
                name
                description
                meta
                flows {
                  edges {
                    node {
                      taskSpecification {
                        slug
                      }
                      next
                    }
                  }
                }
              }
            }
          }
        }
    """

    result = schema.execute(query, variables={"name": workflow_specification.name})

    assert not result.errors
    snapshot.assert_match(result.data)
