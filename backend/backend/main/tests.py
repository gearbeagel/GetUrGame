import os

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
    return User.objects.create_user(
        username="testuser", password="testpass", steam_id="123456789"
    )


@pytest.mark.django_db
def test_main_view(api_client):
    url = reverse("main")
    response = api_client.get(url)
    assert response.status_code == 200
    assert "steam-login" in response.data
    assert "steam-logout" in response.data
    assert "user-games" in response.data
    assert "get-recs" in response.data


@pytest.mark.django_db
def test_csrf_view(api_client):
    url = reverse("csrf")
    response = api_client.get(url)
    assert response.status_code == 200
    assert "csrfToken" in response.json()


@pytest.mark.django_db
def test_steam_login_view(api_client):
    url = reverse("steam-login")
    response = api_client.get(url, {"source": "frontend"})
    assert response.status_code == 200
    assert "redirect_url" in response.data


@pytest.mark.django_db
def test_steam_logout_view(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("steam-logout")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["message"] == "Logged out successfully."


@pytest.mark.django_db
def test_steam_callback_view(api_client, mocker):
    mocker.patch("main.views.get_steam_username", return_value="testuser")
    mocker.patch.dict(
        os.environ, {"STEAM_IDENTITY_URL": os.getenv("STEAM_IDENTITY_URL")}
    )
    url = reverse("steam-callback")
    response = api_client.get(url, {"openid.identity": os.getenv("STEAM_IDENTITY_URL")})
    assert response.status_code == 200
    assert response.data["message"] == "Logged user in successfully"
    assert response.data["steam_id"] == "123456789"
    assert response.data["username"] == "testuser"


@pytest.mark.django_db
def test_check_auth_view(api_client, user, mocker):
    mocker.patch("main.views.get_steam_username", return_value="testuser")
    api_client.force_authenticate(user=user)
    url = reverse("check-auth")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json()["isAuthenticated"] is True
    assert response.json()["username"] == "testuser"


@pytest.mark.django_db
def test_user_games_view(api_client, user, mocker):
    mocker.patch(
        "requests.get",
        return_value=mocker.Mock(
            status_code=200,
            json=lambda: {"response": {"games": [{"appid": 1, "name": "Game 1"}]}},
        ),
    )
    api_client.force_authenticate(user=user)
    url = reverse("user-games")
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Game 1"
