import logging
import os
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
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .decorators import user_not_authenticated
from .models import CustomUser, FavoriteGame
from .serializers import FavoriteGameSerializer, RecommendationSerializer
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ValidationError
from django.http import Http404

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


class CSRFView(APIView):
    """
    View for getting a CSRF token for secure form submissions.

    This endpoint provides a CSRF token that should be included in all POST, PUT,
    PATCH, and DELETE requests to protect against Cross-Site Request Forgery attacks.
    The token should be included in the X-CSRFToken header or as a csrfmiddlewaretoken
    form field in requests to the API.
    """

    def get(self, request):
        """
        Get a CSRF token for the current session.

        Returns:
            JsonResponse: A JSON object containing the CSRF token
        """
        token = get_token(request)
        logger.debug("Generated CSRF token for session")
        return JsonResponse({"csrfToken": token})


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
            logger.debug(f"Session key: {session_key}")
            logger.debug(f"User is authenticated: {request.user.is_authenticated}")

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


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@method_decorator(cache_page(60 * 15), name="get")
class UserGamesView(APIView):
    """
    Fetches the logged-in user's Steam library.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """
        Get the user's Steam library with game details.

        Returns:
            Response: A list of games with details or an error message
        """
        try:
            steam_id = request.user.steam_id
            logger.info(f"Fetching games for user {steam_id}")

            game_details = get_user_games_data(steam_id, include_details=True)

            if not game_details:
                logger.warning(f"No games found for user {steam_id}")
                return Response(
                    {"error": "No games found in your Steam library."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            for game in game_details:
                game["cover_url"] = game.pop("header_image", "")

            paginator = self.pagination_class()
            paginated_games = paginator.paginate_queryset(game_details, request)
            return paginator.get_paginated_response(paginated_games)

        except Exception as e:
            logger.error(f"Error retrieving games: {str(e)}")
            return Response(
                {"error": "Unable to retrieve games from Steam."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def get_steam_game_details(appid):
    """
    Fetch game details from Steam Store API.

    Args:
        appid (int): The Steam AppID of the game

    Returns:
        dict: A dictionary containing game details (short_description, header_image)
    """
    try:
        store_response = requests.get(
            "https://store.steampowered.com/api/appdetails",
            params={"appids": appid},
            timeout=10,
        )
        if store_response.status_code == 200:
            store_data = store_response.json().get(str(appid), {}).get("data", {})
            return {
                "short_description": store_data.get("short_description", "No description available"),
                "header_image": store_data.get(
                    "header_image",
                    f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg",
                ),
            }
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.warning(f"Failed to fetch game details for appid {appid}: {str(e)}")

    # Fallback values if API call fails
    return {
        "short_description": "No description available",
        "header_image": f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg",
    }


def get_user_games_data(steam_id, include_details=False):
    """
    Fetch user's owned games from Steam API.

    Args:
        steam_id (str): The Steam ID of the user
        include_details (bool): Whether to include game details from the Store API

    Returns:
        list: A list of dictionaries containing game information
    """
    try:
        response = requests.get(
            "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/",
            params={
                "key": settings.STEAM_API_KEY,
                "steamid": steam_id,
                "include_appinfo": True,
                "format": "json",
            },
            timeout=15,
        )

        if response.status_code == 200:
            user_games_data = response.json().get("response", {}).get("games", [])

            if not include_details:
                return [{"name": game["name"], "appid": game["appid"]} for game in user_games_data]

            # Include details if requested
            result = []
            for game in user_games_data:
                game_info = {"name": game["name"], "appid": game["appid"]}

                # Get additional details from Steam Store API
                details = get_steam_game_details(game["appid"])
                game_info.update(details)

                result.append(game_info)

            return result

        logger.warning(f"Failed to fetch games for user {steam_id}: Status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching games for user {steam_id}: {str(e)}")

    return []


class RecommendGames(APIView):
    """
    View for getting game recommendations based on the user's entire game library.

    This endpoint uses a machine learning model to recommend games based on the
    user's Steam library. It sends the list of owned games to a FastAPI service
    that runs a RandomForest classifier to find games with similar genre profiles.
    """

    permission_classes = [IsAuthenticated]

    def _get_user_games(self, steam_id):
        """
        Get the user's games and handle the case when no games are found.

        Args:
            steam_id (str): The Steam ID of the user

        Returns:
            tuple: (success, response_or_game_names)
                - If success is True, response_or_game_names is a list of game names
                - If success is False, response_or_game_names is a Response object with an error
        """
        user_games = get_user_games_data(steam_id)

        if not user_games:
            logger.warning(f"No games found for user {steam_id} to generate recommendations")
            return False, Response(
                {"error": "No games found in your Steam library for recommendations"},
                status=status.HTTP_404_NOT_FOUND,
            )

        owned_game_names = [game["name"] for game in user_games]
        return True, owned_game_names

    def _request_recommendations(self, steam_id, owned_game_names):
        """
        Request recommendations from the FastAPI service.

        Args:
            steam_id (str): The Steam ID of the user
            owned_game_names (list): List of game names owned by the user

        Returns:
            tuple: (success, response_or_recommendations)
                - If success is True, response_or_recommendations is a list of recommendations
                - If success is False, response_or_recommendations is a Response object with an error
        """
        try:
            logger.info(f"Requesting recommendations for user {steam_id} with {len(owned_game_names)} games")
            response = requests.post(FASTAPI_URL, json={"game_names": owned_game_names}, timeout=30)

            if response.status_code != 200:
                logger.error(f"FastAPI returned non-200 status code: {response.status_code}")
                return False, Response(
                    {"error": f"Recommendation service returned status code {response.status_code}"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            try:
                data = response.json()
                if "recommendations" not in data:
                    logger.error("FastAPI response missing 'recommendations' key")
                    return False, Response(
                        {"error": "Invalid response from recommendation service"},
                        status=status.HTTP_502_BAD_GATEWAY,
                    )
                recommendations = data["recommendations"]
            except ValueError:
                logger.error("Failed to parse JSON from FastAPI response")
                return False, Response(
                    {"error": "Invalid JSON response from recommendation service"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            return True, recommendations

        except requests.exceptions.Timeout:
            logger.error(f"Timeout while requesting recommendations from {FASTAPI_URL}")
            return False, Response(
                {"error": "Recommendation service timed out"},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error while requesting recommendations from {FASTAPI_URL}")
            return False, Response(
                {"error": "Could not connect to recommendation service"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"FastAPI request failed: {str(e)}")
            return False, Response(
                {"error": f"Recommendation service error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _enrich_recommendations(self, recommendations, steam_id):
        """
        Enrich recommendations with additional details from Steam.

        Args:
            recommendations (list): List of recommendation dictionaries
            steam_id (str): The Steam ID of the user

        Returns:
            list: Enriched recommendations
        """
        for game in recommendations:
            appid = game.get("appid")
            if appid:
                if "short_description" not in game or not game["short_description"]:
                    details = get_steam_game_details(appid)
                    game.update(details)

        logger.info(f"Successfully retrieved {len(recommendations)} recommendations for user {steam_id}")
        return recommendations

    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        """
        Get game recommendations for the authenticated user.

        The recommendations are based on the user's Steam library and use a
        RandomForest classifier to find games with similar genre profiles.

        Returns:
            Response: A list of recommended games or an error message
        """
        steam_id = request.user.steam_id

        success, result = self._get_user_games(steam_id)
        if not success:
            return result
        owned_game_names = result

        favourite_games = request.user.favorite_games.all()
        if favourite_games.exists():
            owned_game_names += [game.name for game in favourite_games]

        success, result = self._request_recommendations(steam_id, owned_game_names)
        if not success:
            return result
        recommendations = result

        recommendations = self._enrich_recommendations(recommendations, steam_id)

        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FavoriteGameView(viewsets.ModelViewSet):
    """
    ViewSet for managing the user's favorite games.
    """

    serializer_class = FavoriteGameSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "appid"
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Return only the current user's favorite games.
        """
        return self.request.user.favorite_games.all()

    def get_object(self):
        """
        Return the specific favorite game for the current user by appid.
        """
        appid = self.kwargs.get(self.lookup_field)
        try:
            if not isinstance(appid, (int, str)) or not str(appid).isdigit():
                raise ValidationError("Invalid appid format")
            return FavoriteGame.objects.get(appid=appid, user=self.request.user)
        except FavoriteGame.DoesNotExist:
            raise Http404("Favorite game not found")

    def create(self, request, *args, **kwargs):
        """
        Add a game to the user's favorites.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Remove a game from the user's favorites.
        """
        favorite_game = self.get_object()
        favorite_game.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
