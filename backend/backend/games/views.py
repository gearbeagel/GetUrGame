import logging
import os

import requests
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RecommendationSerializer
from rest_framework.pagination import PageNumberPagination

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"

logger = logging.getLogger(__name__)

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8080/recommend/")


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
