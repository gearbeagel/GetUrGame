from rest_framework import serializers
from .models import FavoriteGame


class RecommendationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    appid = serializers.IntegerField()
    short_description = serializers.CharField(max_length=1024)
    header_image = serializers.CharField(max_length=255)


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
