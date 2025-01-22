from rest_framework import serializers


class RecommendationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    predicted_score = serializers.FloatField()
    tags = serializers.CharField(max_length=255)
    genres = serializers.CharField(max_length=255)
    AppID = serializers.IntegerField()
    reviews = serializers.CharField(max_length=1024)
    short_description = serializers.CharField(max_length=1024)
    header_image = serializers.CharField(max_length=255)
