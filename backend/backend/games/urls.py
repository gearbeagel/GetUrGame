from django.urls import path
from .views import RecommendGames, UserGamesView

urlpatterns = [
    path("", UserGamesView.as_view(), name="user-games"),
    path("recommend/", RecommendGames.as_view(), name="get-recs"),
]
