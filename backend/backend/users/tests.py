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
def test_valid_steam_callback_creates_user_and_logs_in(mocker, api_client):
    mocker.patch("users.views.get_steam_username", return_value="TestUser")

    steam_id = "76561198000000000"
    callback_url = reverse("steam-callback")
    openid_identity = f"https://steamcommunity.com/openid/id/{steam_id}"

    params = {
        "openid.identity": openid_identity,
        "openid.claimed_id": openid_identity,
        "openid.mode": "id_res",
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.return_to": "http://testserver/api/steam/callback",
    }

    response = api_client.get(callback_url, params)

    assert response.status_code == 200
    data = response.json()
    assert data["steam_id"] == steam_id
    assert data["username"] == "TestUser"


@pytest.mark.django_db
def test_check_auth_view(api_client, user, mocker):
    mocker.patch("users.views.get_steam_username", return_value="testuser")
    api_client.force_authenticate(user=user)
    url = reverse("check-auth")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json()["isAuthenticated"] is True
    assert response.json()["username"] == "testuser"
