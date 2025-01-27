from django.urls import path
from .views import (CheckAuthView, RecommendGames, SteamCallbackView,
                    SteamLoginView, SteamLogoutView, UserGamesView)

urlpatterns = [
    path("steam/login/", SteamLoginView.as_view(), name="steam-login"),
    path("steam/logout/", SteamLogoutView.as_view(), name="steam-logout"),
    path("steam/callback/", SteamCallbackView.as_view(), name="steam-callback"),
    path("user/games/", UserGamesView.as_view(), name="user-games"),
    path("get-recs/", RecommendGames.as_view(), name="get-recs"),
    path("misc/check-auth/", CheckAuthView.as_view(), name="check-auth"),
]
