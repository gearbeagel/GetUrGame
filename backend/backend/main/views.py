import logging

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from urllib.parse import urlencode
import requests

from .models import CustomUser

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"


class MainView(APIView):
    """
    Main View.
    """

    def get(self, request):
        links = {
            "steam-login": request.build_absolute_uri(reverse('steam-login')),
            "steam-logout": request.build_absolute_uri(reverse('steam-logout')),
            "user-games": request.build_absolute_uri(reverse('user-games')),
        }
        return Response(links)


class SteamLoginView(APIView):
    """
    Initiates the Steam OpenID login process.
    """

    def get(self, request):
        params = {
            'openid.ns': 'http://specs.openid.net/auth/2.0',
            'openid.mode': 'checkid_setup',
            'openid.return_to': request.build_absolute_uri('/api/steam/callback/'),
            'openid.realm': request.build_absolute_uri('/'),
            'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
            'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
        }
        steam_url = f"{STEAM_OPENID_URL}?{urlencode(params)}"
        return Response({"redirect_url": steam_url})


class SteamLogoutView(APIView):
    """
    Logs the user out of the application.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."})


def get_steam_username(steam_id):
    """
    Fetches the username of a Steam user by their Steam ID.
    """
    api_key = settings.STEAM_API_KEY
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {
        'key': api_key,
        'steamids': steam_id,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'response' in data and 'players' in data['response']:
            player_data = data['response']['players'][0]
            return player_data.get('personaname', 'No username found')
    return None


def validate_openid_response(params):
    try:
        validation_url = "https://steamcommunity.com/openid/login"
        validation_params = params.copy()
        validation_params['openid.mode'] = 'check_authentication'
        response = requests.post(validation_url, data=validation_params)

        # Log the validation request and response for debugging
        logger.debug("Validation request: %s", validation_params)
        logger.debug("Validation response: %s", response.text)

        return 'is_valid:true' in response.text
    except Exception as e:
        logger.error("Validation error: %s", e)
        return False


logger = logging.getLogger(__name__)


class SteamCallbackView(APIView):
    """
    Handles the Steam OpenID callback.
    """
    def get(self, request):
        openid_params = request.GET
        logger.debug("Received OpenID params: %s", openid_params)

        if not validate_openid_response(openid_params):
            logger.error("OpenID response validation failed.")
            return Response({"error": "Invalid OpenID response."}, status=400)

        try:
            steam_id = openid_params['openid.identity'].split('/')[-1]
            username = get_steam_username(steam_id)
            logger.info("Steam user authenticated: %s (%s)", username, steam_id)

            user, created = CustomUser.objects.get_or_create(steam_id=steam_id)
            if created and username:
                logger.debug("Created new user: %s", username)
                user.username = username
                user.set_unusable_password()
                user.save()

            login(request, user)
            return Response({"message": "Logged in successfully.", "steam_id": steam_id, "username": username})

        except Exception as e:
            logger.error("Error during Steam callback: %s", str(e))
            return Response({"error": f"An error occurred: {str(e)}"}, status=500)


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
                'key': settings.STEAM_API_KEY,
                'steamid': steam_id,
                'include_appinfo': True,
                'format': 'json',
            }
        )
        if response.status_code == 200:
            games_data = response.json().get('response', {}).get('games', [])
            game_details = []

            for game in games_data:
                appid = game['appid']
                store_response = requests.get(
                    "https://store.steampowered.com/api/appdetails",
                    params={"appids": appid}
                )
                if store_response.status_code == 200:
                    store_data = store_response.json().get(str(appid), {}).get("data", {})
                    short_description = store_data.get('short_description', 'No description available')
                    cover_url = store_data.get('header_image',
                                               f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg")
                else:
                    short_description = 'No description available'
                    cover_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg"

                game_details.append({
                    'name': game['name'],
                    'short_description': short_description,
                    'cover_url': cover_url,
                    'appid': appid,
                })
            return Response({"games": game_details})

        return Response({"error": "Unable to retrieve games."}, status=500)
