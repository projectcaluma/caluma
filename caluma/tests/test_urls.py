from django.urls import reverse


def test_graphql_url(client):
    assert reverse("graphql")
