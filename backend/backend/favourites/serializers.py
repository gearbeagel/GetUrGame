from rest_framework import serializers
from favourites.models import FavoriteGame


class FavoriteGameSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = FavoriteGame
        fields = ["id", "appid", "name", "header_image", "short_description", "user"]

    def validate_appid(self, value):
        if not value:
            raise serializers.ValidationError("App ID is required.")
        return value

    def create(self, validated_data):
        user = validated_data.pop("user")
        favorite_game = FavoriteGame.objects.create(user=user, **validated_data)
        return favorite_game
