"""
Green Match models.

Note: the master Plant model lives in `apps.plants.models` because both
the Green Match feature and the Plants feature need it. Here we only
define the per-user MatchSession history.
"""
import uuid
from django.db import models
from django.conf import settings


class MatchSession(models.Model):
    """A historical record of one Green Match query a user ran."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='match_sessions',
    )
    location = models.CharField(max_length=255)
    sun_exposure = models.CharField(max_length=30)
    soil_condition = models.CharField(max_length=50)
    water_conservation = models.CharField(max_length=20)
    climate_zone = models.CharField(max_length=50, blank=True)
    top_match_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} @ {self.location} ({self.created_at:%Y-%m-%d})'
