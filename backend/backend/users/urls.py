from django.urls import path
from .views import CSRFView, CheckAuthView, SteamCallbackView, SteamLoginView, SteamLogoutView

urlpatterns = [
    path("steam/login/", SteamLoginView.as_view(), name="steam-login"),
    path("steam/logout/", SteamLogoutView.as_view(), name="steam-logout"),
    path("steam/callback/", SteamCallbackView.as_view(), name="steam-callback"),
    path("misc/check-auth/", CheckAuthView.as_view(), name="check-auth"),
    path("csrf/", CSRFView.as_view(), name="csrf"),
]
