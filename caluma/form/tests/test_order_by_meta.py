import pytest


@pytest.mark.parametrize(
    "factory,query,reverse",
    [
        ("case_factory", "allCases", True),
        ("case_factory", "allCases", False),
        ("document_factory", "allDocuments", True),
        ("document_factory", "allDocuments", False),
    ],
)
def test_order_by_meta(db, schema_executor, request, factory, query, reverse):

    factory = request.getfixturevalue(factory)
    factory(meta={"test-key": 3})
    factory(meta={"test-key": 100})
    factory(meta={"test-key": 20})

    order = "META_TEST_KEY_DESC" if reverse else "META_TEST_KEY_ASC"

    resp = schema_executor(
        f"""
            query {{
                {query} (orderBy: {order}) {{
                    edges {{
                        node {{
                            meta
                        }}
                    }}
                }}
            }}
        """
    )

    assert not resp.errors

    edges = resp.data[query]["edges"]

    assert edges == sorted(
        edges, key=lambda e: e["node"]["meta"]["test-key"], reverse=reverse
    )
