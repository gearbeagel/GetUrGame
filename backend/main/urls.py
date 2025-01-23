from django.urls import path, include
from .views import SteamLoginView, SteamLogoutView, SteamCallbackView, UserGamesView, MainView, RecommendGames

urlpatterns = [
    path('steam/login/', SteamLoginView.as_view(), name='steam-login'),
    path('steam/logout/', SteamLogoutView.as_view(), name='steam-logout'),
    path('steam/callback/', SteamCallbackView.as_view(), name='steam-callback'),
    path('user/games/', UserGamesView.as_view(), name='user-games'),
    path('get-recs/', RecommendGames.as_view(), name='get-recs'),
]
