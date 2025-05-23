from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ValidationError
from django.http import Http404
from favourites.models import FavoriteGame
from favourites.serializers import FavoriteGameSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class FavoriteGameView(viewsets.ModelViewSet):
    serializer_class = FavoriteGameSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "appid"
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.request.user.favorite_games.all()

    def get_object(self):
        appid = self.kwargs.get(self.lookup_field)
        try:
            if not isinstance(appid, (int, str)) or not str(appid).isdigit():
                raise ValidationError("Invalid appid format")
            return FavoriteGame.objects.get(appid=appid, user=self.request.user)
        except FavoriteGame.DoesNotExist:
            raise Http404("Favorite game not found")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    def destroy(self, request, *args, **kwargs):
        favorite_game = self.get_object()
        favorite_game.delete()
        return Response(status=204)
