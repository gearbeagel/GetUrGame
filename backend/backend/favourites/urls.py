from django.urls import path
from .views import FavoriteGameView
from django.urls import include

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"favourites", FavoriteGameView, basename="user-favorite-games")

urlpatterns = [
    path("", include(router.urls)),
]
