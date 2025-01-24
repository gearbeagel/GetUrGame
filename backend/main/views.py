import logging

import kagglehub
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from urllib.parse import urlencode
import requests
from data.model import get_keras_model, preprocess_data, get_tfidf_and_scaler
import numpy as np
import pandas as pd
from django.conf import settings

from .models import CustomUser
from .serializers import RecommendationSerializer

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
            "get-recs": request.build_absolute_uri(reverse('get-recs')),
        }
        return Response(links)


class SteamLoginView(APIView):
    """
    Initiates the Steam OpenID login process.
    """

    def get(self, request):
        try:
            is_frontend = request.GET.get('source') == 'frontend'
            return_to_url = (
                "http://localhost:5173/steam/callback" if is_frontend
                else "http://localhost:8000/api/steam/callback"
            )

            params = {
                'openid.ns': 'http://specs.openid.net/auth/2.0',
                'openid.mode': 'checkid_setup',
                'openid.return_to': "http://localhost:5173/steam/callback",
                'openid.realm': "http://localhost:5173/steam/callback",
                'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
                'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
            }
            steam_url = f"{STEAM_OPENID_URL}?{urlencode(params)}"
            return JsonResponse({"redirect_url": steam_url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class SteamLogoutView(APIView):
    """
    Logs the user out of the application.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."})


logger = logging.getLogger(__name__)


class SteamCallbackView(APIView):
    """
    Handles the Steam OpenID callback.
    """

    def get(self, request):
        try:
            openid_params = request.GET
            logger.debug("Received OpenID params: %s", openid_params)

            if not self.validate_openid_response(openid_params):
                logger.error("OpenID response validation failed.")
                return Response({"error": "Invalid OpenID response."}, status=400)

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

    def validate_openid_response(self, params):
        try:
            validation_url = "https://steamcommunity.com/openid/login"
            validation_params = params.copy()
            validation_params['openid.mode'] = 'check_authentication'
            response = requests.post(validation_url, data=validation_params)
            return 'is_valid:true' in response.text
        except Exception as e:
            logger.error("Validation error: %s", e)
            return False


def get_steam_username(steam_id):
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


class CheckAuthView(APIView):
    """
    Checks if the user is authenticated.
    """

    def get(self, request):
        if request.user.is_authenticated:
            username = get_steam_username(request.user.steam_id)
            return JsonResponse({"isAuthenticated": True, "username": username})
        return JsonResponse({"isAuthenticated": False, "username": None})


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


def get_user_games_data(steam_id):
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
        user_games_data = response.json().get('response', {}).get('games', [])
        return [{'name': game['name'], 'appid': game['appid']} for game in user_games_data]
    return []


class RecommendGames(APIView):
    """
    View for getting recommendations.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Get your own recommendations!"})

    def post(self, request):
        steam_id = request.user.steam_id
        user_games = get_user_games_data(steam_id)

        if not user_games:
            return Response({'error': 'Unable to retrieve games for recommendations'},
                            status=status.HTTP_400_BAD_REQUEST)

        model = get_keras_model()
        path = kagglehub.dataset_download('artermiloff/steam-games-dataset')
        df = pd.read_csv(path + '/games_may2024_cleaned.csv')
        df = preprocess_data(df)

        tfidf, scaler = get_tfidf_and_scaler(df)
        owned_game_names = [game['name'] for game in user_games]
        filtered_df = df[~df['name'].isin(owned_game_names)]

        combined_features_tfidf = tfidf.transform(filtered_df['combined_features'])
        additional_features = filtered_df[['review_sentiment', 'estimated_owners_processed']].to_numpy()

        game_features = np.hstack([combined_features_tfidf.toarray(), additional_features])
        game_features_scaled = scaler.transform(game_features)

        predicted_scores = model.predict(game_features_scaled, verbose=0)

        filtered_df['predicted_score'] = predicted_scores

        recommendations = (
            filtered_df[['name', 'predicted_score', 'tags', 'genres', 'AppID', 'reviews', 'short_description',
                         'header_image']]
            .sort_values('predicted_score', ascending=False)
            .head(200)
            .sample(5)
            .to_dict(orient='records')
        )

        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
