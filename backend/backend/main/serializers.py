from rest_framework import serializers


class RecommendationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    appid = serializers.IntegerField()
    short_description = serializers.CharField(max_length=1024)
    header_image = serializers.CharField(max_length=255)
