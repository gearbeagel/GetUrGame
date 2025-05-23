from django.db import models
from users.models import CustomUser


class FavoriteGame(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="favorite_games")
    appid = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    short_description = models.TextField()
    header_image = models.URLField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.appid})"
