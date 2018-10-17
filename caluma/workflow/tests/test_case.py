def test_query_all_cases(db, snapshot, case, flow, schema_executor):
    query = """
        query AllCases {
          allCases {
            edges {
              node {
                status
              }
            }
          }
        }
    """

    result = schema_executor(query)

    assert not result.errors
    snapshot.assert_match(result.data)


def test_start_case(db, snapshot, workflow, schema_executor):
    query = """
        mutation StartCase($input: StartCaseInput!) {
          startCase(input: $input) {
            case {
              document {
                form {
                  slug
                }
              }
              status
              workItems {
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

    inp = {"input": {"workflow": workflow.slug}}
    result = schema_executor(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)
