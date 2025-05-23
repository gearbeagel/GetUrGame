from django.urls import include, path

urlpatterns = [
    path("user/", include("users.urls")),
    path("games/", include("games.urls")),
    path("favourites/", include("favourites.urls")),
]
