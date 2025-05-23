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
def test_user_games_view(api_client, user, mocker):
    mocker.patch(
        "requests.get",
        return_value=mocker.Mock(
            status_code=200, json=lambda: {"response": {"games": [{"appid": 1, "name": "Game 1"}]}}
        ),
    )
    api_client.force_authenticate(user=user)
    url = reverse("user-games")
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "Game 1"


@pytest.mark.django_db
def test_get_recommendations(api_client, user, mocker):
    mocker.patch("games.views.get_user_games_data", return_value=[{"name": "Game 1", "appid": 1}])
    mocker.patch(
        "requests.post",
        return_value=mocker.Mock(
            status_code=200, json=lambda: {"recommendations": [{"name": "Rec Game", "appid": 2}]}
        ),
    )
    mocker.patch(
        "games.views.get_steam_game_details", return_value={"short_description": "desc", "header_image": "url"}
    )
    api_client.force_authenticate(user=user)
    url = reverse("get-recs")
    response = api_client.post(url)
    assert response.status_code == 200
    assert any(r["name"] == "Rec Game" for r in response.data)


@pytest.mark.django_db
def test_get_recommendations_no_games(api_client, user, mocker):
    mocker.patch("games.views.get_user_games_data", return_value=[])
    api_client.force_authenticate(user=user)
    url = reverse("get-recs")
    response = api_client.post(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_get_recommendations_no_recommendations(api_client, user, mocker):
    mocker.patch("games.views.get_user_games_data", return_value=[{"name": "Game 1", "appid": 1}])
    mocker.patch(
        "requests.post",
        return_value=mocker.Mock(status_code=200, json=lambda: {"recommendations": []}),
    )
    api_client.force_authenticate(user=user)
    url = reverse("get-recs")
    response = api_client.post(url)
    assert response.status_code == 200
    assert response.data == []
