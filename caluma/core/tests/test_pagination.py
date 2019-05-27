def test_offset_pagination(db, schema_executor, document_factory):
    document_factory(meta={"position": 0})
    document_factory(meta={"position": 1})
    document_factory(meta={"position": 2})
    document_factory(meta={"position": 3})
    document_factory(meta={"position": 4})

    query = """
        query AllDocumentsQuery {
          allDocuments(limit: 2, offset: 2) {
            totalCount
            edges {
              node {
                id
                meta
              }
            }
          }
        }
    """

    result = schema_executor(query)

    assert not result.errors
    assert len(result.data["allDocuments"]["edges"]) == 2
    assert result.data["allDocuments"]["totalCount"] == 2
    assert result.data["allDocuments"]["edges"][0]["node"]["meta"]["position"] == 2
    assert result.data["allDocuments"]["edges"][1]["node"]["meta"]["position"] == 3
