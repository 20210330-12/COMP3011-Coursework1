from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    display_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    favourite_team = models.ForeignKey(
        "football.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fans"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.user.username