import logging
import os
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import APIView
from dotenv import load_dotenv

load_dotenv()

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"

logger = logging.getLogger(__name__)

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8080/recommend/")


class MainView(APIView):
    """
    Main API entry point that provides links to all available endpoints.

    This view serves as the API root and provides a list of all available
    endpoints with their absolute URLs. It helps clients discover the API
    structure and available resources.
    """

    def get(self, request):
        """
        Get a list of all available API endpoints.

        Returns:
            Response: A dictionary of endpoint names and their absolute URLs
        """
        links = {
            "steam-login": request.build_absolute_uri(reverse("steam-login")),
            "steam-logout": request.build_absolute_uri(reverse("steam-logout")),
            "user-games": request.build_absolute_uri(reverse("user-games")),
            "user-favorites": request.build_absolute_uri(reverse("user-favorite-games")),
            "get-recs": request.build_absolute_uri(reverse("get-recs")),
            "check-auth": request.build_absolute_uri(reverse("check-auth")),
            "csrf": request.build_absolute_uri(reverse("csrf")),
        }

        descriptions = {
            "steam-login": "Initiates the Steam OpenID login process",
            "steam-logout": "Logs the user out of the application",
            "user-games": "Fetches the logged-in user's Steam library",
            "user-favorites": "Fetches the user's favorite games",
            "get-recs": "Gets game recommendations based on the user's library",
            "check-auth": "Checks if the user is authenticated",
            "csrf": "Gets a CSRF token for form submissions",
        }

        response_data = {
            "api_name": "GetUrGame API",
            "version": "1.0",
            "endpoints": links,
            "descriptions": descriptions,
        }

        return Response(response_data)
