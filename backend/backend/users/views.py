import logging
from urllib.parse import urlencode
import requests
from django.conf import settings
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser
from main.decorators import user_not_authenticated
from dotenv import load_dotenv

load_dotenv()

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
logger = logging.getLogger(__name__)


class CSRFView(APIView):
    def get(self, request):
        token = get_token(request)
        logger.debug("Generated CSRF token for session")
        return JsonResponse({"csrfToken": token})


@method_decorator(user_not_authenticated, name="get")
class SteamLoginView(APIView):
    @method_decorator(require_GET)
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
    @method_decorator(require_GET)
    def get(self, request):
        try:
            openid_params = request.GET
            logger.info("Received OpenID params: %s", openid_params)
            openid_identity = openid_params.get("openid.identity")
            if not openid_identity or not openid_identity.startswith("https://steamcommunity.com/openid/id/"):
                logger.warning("Invalid openid.identity: %s", openid_identity)
                return Response({"error": "Invalid OpenID response."}, status=400)
            steam_id = openid_identity.split("/")[-1]
            if not steam_id.isdigit():
                logger.warning("Non-numeric steam_id in OpenID response: %s", steam_id)
                return Response({"error": "Invalid Steam ID."}, status=400)
            username = get_steam_username(steam_id)
            if not username:
                logger.warning("Could not fetch username for steam_id: %s", steam_id)
                return Response({"error": "Could not fetch Steam username."}, status=400)
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
            return Response({"error": "An error occurred."}, status=500)


def get_steam_username(steam_id):
    api_key = settings.STEAM_API_KEY
    if not api_key:
        logger.error("STEAM_API_KEY is not set.")
        return None
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {
        "key": api_key,
        "steamids": steam_id,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "response" in data and "players" in data["response"] and data["response"]["players"]:
                player_data = data["response"]["players"][0]
                return player_data.get("personaname", "No username found")
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch Steam username: {str(e)}")
    return None


class CheckAuthView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            username = get_steam_username(request.user.steam_id)
            logger.info("User is authenticated: %s", username)
            return JsonResponse({"isAuthenticated": True, "username": username})
        logger.info("User is not authenticated")
        return JsonResponse({"isAuthenticated": False, "username": None})
