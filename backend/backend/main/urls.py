from django.urls import include, path
from .views import (
    CSRFView,
    CheckAuthView,
    FavoriteGameView,
    RecommendGames,
    SteamCallbackView,
    SteamLoginView,
    SteamLogoutView,
    UserGamesView,
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"user/favorites", FavoriteGameView, basename="user-favorite-games")

urlpatterns = [
    path("", include(router.urls)),
    path("csrf/", CSRFView.as_view(), name="csrf"),
    path("steam/login/", SteamLoginView.as_view(), name="steam-login"),
    path("steam/logout/", SteamLogoutView.as_view(), name="steam-logout"),
    path("steam/callback/", SteamCallbackView.as_view(), name="steam-callback"),
    path("user/games/", UserGamesView.as_view(), name="user-games"),
    path("get-recs/", RecommendGames.as_view(), name="get-recs"),
    path("misc/check-auth/", CheckAuthView.as_view(), name="check-auth"),
]
