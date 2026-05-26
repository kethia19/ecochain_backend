# Create your models here.
"""
SavedRecommendation — generic store for both build layouts and cost estimates.
The `recommendation_type` field distinguishes them; `data` holds the full payload.
"""
import uuid
from django.db import models
from django.conf import settings


class SavedRecommendation(models.Model):
    TYPE_CHOICES = [
        ('layout', 'Build Layout'),
        ('cost_estimate', 'Cost Estimate'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_recommendations',
    )
    recommendation_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200, blank=True)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'recommendation_type']),
        ]

    def __str__(self):
        return f'{self.user} — {self.recommendation_type} — {self.title or self.id}'

    def save(self, *args, **kwargs):
        # Auto-generate title if none provided
        if not self.title:
            if self.recommendation_type == 'layout':
                bedrooms = self.data.get('bedrooms') or self.data.get('rooms') or '?'
                zone = self.data.get('climate_zone') or self.data.get('country') or 'custom'
                self.title = f'{bedrooms}-bedroom {zone} layout'
            else:
                country = self.data.get('country', 'house')
                size = self.data.get('size', '?')
                self.title = f'{size}sqm {country} estimate'
        super().save(*args, **kwargs)