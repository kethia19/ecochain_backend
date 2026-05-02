"""
Impact log — aggregated water/CO2 metrics rendered on the dashboard.
"""
import uuid
from django.db import models
from django.conf import settings


class ImpactLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='impact_logs',
    )
    water_saved_litres = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    co2_offset_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email}: {self.water_saved_litres}L / {self.co2_offset_kg}kg'
