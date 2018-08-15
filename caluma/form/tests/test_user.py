from django.urls import reverse
from rest_framework import status


def test_user_detail(admin_user, admin_client):
    url = reverse("user-detail", args=[admin_user.id])

    response = admin_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    json = response.json()
    assert json["data"]["id"] == str(admin_user.id)
    assert "password" not in json["data"]["attributes"]
