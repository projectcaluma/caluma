from ...schema import schema


def test_query_all_cases(db, snapshot, case, flow):
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

    result = schema.execute(query)

    assert not result.errors
    snapshot.assert_match(result.data)


def test_start_case(db, snapshot, workflow):
    query = """
        mutation StartCase($input: StartCaseInput!) {
          startCase(input: $input) {
            case {
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
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)
