from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    steam_id = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def __str__(self):
        return self.username


class FavoriteGame(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="favorite_games")
    appid = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    short_description = models.TextField()
    header_image = models.URLField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.appid})"
