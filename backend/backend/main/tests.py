import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_main_view_returns_api_info():
    client = APIClient()
    url = reverse("main")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "api_name" in data
    assert "version" in data
    assert "endpoints" in data
    assert "descriptions" in data
    expected_keys = ["steam-login", "steam-logout", "user-games", "user-favorites", "get-recs", "check-auth", "csrf"]
    for key in expected_keys:
        assert key in data["endpoints"]
        assert key in data["descriptions"]


@pytest.mark.django_db
def test_main_view_links_are_absolute():
    client = APIClient()
    url = reverse("main")
    response = client.get(url)
    data = response.json()
    for endpoint_url in data["endpoints"].values():
        assert endpoint_url.startswith("http"), f"Endpoint URL is not absolute: {endpoint_url}"
