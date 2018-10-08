from ...schema import schema


def test_query_all_workflows(db, snapshot, workflow, flow):
    query = """
        query AllWorkflows {
          allWorkflows {
            edges {
              node {
                status
              }
            }
          }
        }
    """

    result = schema.execute(query)

    assert not result.errors
    snapshot.assert_match(result.data)


def test_start_workflow(db, snapshot, workflow_specification):
    query = """
        mutation StartWorkflow($input: StartWorkflowInput!) {
          startWorkflow(input: $input) {
            workflow {
              form {
                formSpecification {
                  slug
                }
              }
              status
              tasks {
                edges {
                  node {
                    status
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    inp = {"input": {"workflowSpecification": workflow_specification.slug}}
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)
