import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpass", steam_id="123456789")


@pytest.mark.django_db
def test_create_favorite_game(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("user-favorite-games-list")
    data = {
        "appid": 123,
        "name": "Fav Game",
        "header_image": "http://example.com/image.jpg",
        "short_description": "A great game",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["name"] == "Fav Game"


@pytest.mark.django_db
def test_list_favorite_games(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("user-favorite-games-list")
    api_client.post(
        url,
        {
            "appid": 123,
            "name": "Fav Game",
            "header_image": "http://example.com/image.jpg",
            "short_description": "A great game",
        },
        format="json",
    )
    response = api_client.get(url)
    assert response.status_code == 200
    assert any(f["appid"] == 123 for f in response.data["results"])


@pytest.mark.django_db
def test_delete_favorite_game(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("user-favorite-games-list")
    api_client.post(
        url,
        {
            "appid": 123,
            "name": "Fav Game",
            "header_image": "http://example.com/image.jpg",
            "short_description": "A great game",
        },
        format="json",
    )
    del_url = reverse("user-favorite-games-detail", args=[123])
    response = api_client.delete(del_url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_list_favorite_games_empty(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("user-favorite-games-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["results"] == []
