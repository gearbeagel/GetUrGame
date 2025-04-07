import logging
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .decorators import user_not_authenticated
from .models import CustomUser
from .serializers import RecommendationSerializer

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"

logger = logging.getLogger(__name__)

FASTAPI_URL = "http://gyg-model:8080/recommend/"


class MainView(APIView):
    """
    Main View.
    """

    def get(self, request):
        links = {
            "steam-login": request.build_absolute_uri(reverse("steam-login")),
            "steam-logout": request.build_absolute_uri(reverse("steam-logout")),
            "user-games": request.build_absolute_uri(reverse("user-games")),
            "get-recs": request.build_absolute_uri(reverse("get-recs")),
        }
        return Response(links)


class CSRFView(APIView):
    """
    View for getting CSRF token.
    """

    def get(self, request):
        return JsonResponse({"csrfToken": get_token(request)})


@method_decorator(user_not_authenticated, name="get")
class SteamLoginView(APIView):
    """
    Initiates the Steam OpenID login process.
    """

    def get(self, request):
        try:
            is_frontend = request.GET.get("source") == "frontend"
            return_to_url = (
                f"{settings.FRONTEND_URL}/steam/callback"
                if is_frontend
                else f"{settings.BACKEND_URL}/api/steam/callback"
            )

            params = {
                "openid.ns": "http://specs.openid.net/auth/2.0",
                "openid.mode": "checkid_setup",
                "openid.return_to": return_to_url,
                "openid.realm": return_to_url,
                "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
                "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
            }

            steam_url = f"{STEAM_OPENID_URL}?{urlencode(params)}"
            logger.info("Redirecting to Steam for authentication: %s", steam_url)

            return Response({"redirect_url": steam_url})

        except Exception as e:
            logger.error(f"Error in SteamLoginView: {str(e)}")
            return Response({"error": "An error occurred during login."}, status=500)


class SteamLogoutView(APIView):
    """
    Logs the user out of the application.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            logout(request)
            logger.info("User logged out successfully.")
            return Response({"message": "Logged out successfully."})
        except Exception as e:
            logger.error(f"Logout incomplete: {str(e)}")
            return Response({"message": "Logout incomplete."}, status=500)


class SteamCallbackView(APIView):
    """
    Handles the Steam OpenID callback and processes the user authentication.
    """

    def get(self, request):
        try:
            openid_params = request.GET
            logger.info("Received OpenID params: %s", openid_params)

            steam_id = openid_params["openid.identity"].split("/")[-1]
            username = get_steam_username(steam_id)

            user, created = CustomUser.objects.get_or_create(steam_id=steam_id)
            if created:
                logger.debug("Created new user: %s", username)
                user.username = username
                user.set_unusable_password()
                user.save()

            login(request, user)
            logger.info("User logged in successfully: %s", username)

            session_key = request.session.session_key
            print(f"Session key: {session_key}")
            print(f"User is authenticated: {request.user.is_authenticated}")

            return Response(
                {
                    "message": "Logged user in successfully",
                    "steam_id": steam_id,
                    "username": username,
                }
            )

        except Exception as e:
            logger.error("Error during Steam callback: %s", str(e))
            return Response({"error": f"An error occurred: {str(e)}"}, status=500)


def get_steam_username(steam_id):
    api_key = settings.STEAM_API_KEY
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {
        "key": api_key,
        "steamids": steam_id,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "response" in data and "players" in data["response"]:
            player_data = data["response"]["players"][0]
            return player_data.get("personaname", "No username found")
    return None


class CheckAuthView(APIView):
    """
    Checks if the user is authenticated.
    """

    def get(self, request):
        if request.user.is_authenticated:
            username = get_steam_username(request.user.steam_id)
            logger.info("User is authenticated: %s", username)
            return JsonResponse({"isAuthenticated": True, "username": username})
        logger.info("User is not authenticated")
        return JsonResponse({"isAuthenticated": False, "username": None})


@method_decorator(cache_page(60 * 15), name="get")
class UserGamesView(APIView):
    """
    Fetches the logged-in user's Steam library.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        steam_id = request.user.steam_id
        response = requests.get(
            "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/",
            params={
                "key": settings.STEAM_API_KEY,
                "steamid": steam_id,
                "include_appinfo": True,
                "format": "json",
            },
        )
        if response.status_code == 200:
            games_data = response.json().get("response", {}).get("games", [])
            game_details = []
            for game in games_data:
                appid = game["appid"]
                store_response = requests.get(
                    "https://store.steampowered.com/api/appdetails",
                    params={"appids": appid},
                )
                if store_response.status_code == 200:
                    store_data = (
                        store_response.json().get(str(appid), {}).get("data", {})
                    )
                    short_description = store_data.get(
                        "short_description", "No description available"
                    )
                    cover_url = store_data.get(
                        "header_image",
                        f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg",
                    )
                else:
                    short_description = "No description available"
                    cover_url = (
                        f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg"
                    )
                game_details.append(
                    {
                        "name": game["name"],
                        "short_description": short_description,
                        "cover_url": cover_url,
                        "appid": appid,
                    }
                )
            return Response(game_details)

        return Response({"error": "Unable to retrieve games."}, status=500)


def get_user_games_data(steam_id):
    response = requests.get(
        "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/",
        params={
            "key": settings.STEAM_API_KEY,
            "steamid": steam_id,
            "include_appinfo": True,
            "format": "json",
        },
    )
    if response.status_code == 200:
        user_games_data = response.json().get("response", {}).get("games", [])
        return [
            {"name": game["name"], "appid": game["appid"]} for game in user_games_data
        ]
    return []


class RecommendGames(APIView):
    """
    View for getting game recommendations based on the user's entire game library.
    """

    permission_classes = [IsAuthenticated]

    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        steam_id = request.user.steam_id
        user_games = get_user_games_data(steam_id)

        if not user_games:
            return Response(
                {"error": "Unable to retrieve games for recommendations"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        owned_game_names = [game["name"] for game in user_games]

        try:
            response = requests.post(FASTAPI_URL, json={"game_names": owned_game_names})
            response.raise_for_status()
            recommendations = response.json()["recommendations"]
            for game in recommendations:
                game[
                    "header_image"
                ] = f"https://steamcdn-a.akamaihd.net/steam/apps/{game['appid']}/header.jpg"
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"FastAPI request failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
