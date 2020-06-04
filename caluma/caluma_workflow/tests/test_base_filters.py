def test_base_model_created_by_user_filter(db, work_item_factory, schema_executor):
    work_item_factory(created_by_user="Winston Smith")
    work_item_factory(created_by_user="Martin")

    query = """
            query WorkItems($createdByUser: String!) {
              allWorkItems(createdByUser: $createdByUser) {
                edges {
                  node {
                    createdByUser
                    createdByGroup
                  }
                }
              }
            }
        """

    result = schema_executor(query, variable_values={"createdByUser": "Winston Smith"})

    assert not result.errors
    assert len(result.data["allWorkItems"]["edges"]) == 1
    assert (
        result.data["allWorkItems"]["edges"][0]["node"]["createdByUser"]
        == "Winston Smith"
    )


def test_base_model_created_by_group_filter(db, work_item_factory, schema_executor):
    work_item_factory(created_by_group="Oceania")
    work_item_factory(created_by_group="Eurasia")

    query = """
                query WorkItems($createdByGroup: String!) {
                  allWorkItems(createdByGroup: $createdByGroup) {
                    edges {
                      node {
                        createdByUser
                        createdByGroup
                      }
                    }
                  }
                }
            """

    result = schema_executor(query, variable_values={"createdByGroup": "Oceania"})

    assert not result.errors
    assert len(result.data["allWorkItems"]["edges"]) == 1
    assert (
        result.data["allWorkItems"]["edges"][0]["node"]["createdByGroup"] == "Oceania"
    )
