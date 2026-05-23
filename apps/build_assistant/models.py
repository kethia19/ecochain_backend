import uuid
from django.db import models
from django.conf import settings


class ClimateZone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    typical_countries = models.JSONField(default=list)
    cooling_strategy = models.CharField(max_length=255, blank=True)
    passive_features = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class EcoMaterial(models.Model):
    ELEMENT_CHOICES = [
        ('wall', 'Wall'),
        ('foundation', 'Foundation'),
        ('roof', 'Roof'),
        ('floor', 'Floor'),
        ('window', 'Window'),
        ('insulation', 'Insulation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    element_type = models.CharField(max_length=50, choices=ELEMENT_CHOICES)
    description = models.TextField(blank=True)
    sustainability_rationale = models.TextField(blank=True)
    carbon_score = models.FloatField(default=0.0)
    cost_delta_pct = models.FloatField(default=0.0)
    suitable_climate_zones = models.JSONField(default=list)
    is_eco_alternative = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['element_type', 'name']

    def __str__(self):
        return f'{self.name} ({self.element_type})'


class Layout(models.Model):
    STYLE_CHOICES = [
        ('modern', 'Modern'),
        ('traditional', 'Traditional'),
        ('hybrid', 'Hybrid'),
    ]
    ORIENTATION_CHOICES = [
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='layouts',
    )
    name = models.CharField(max_length=255, blank=True)
    bedrooms = models.IntegerField()
    climate_zone = models.CharField(max_length=50)
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='modern')
    orientation = models.CharField(max_length=20, choices=ORIENTATION_CHOICES, default='south')
    layout_json = models.JSONField(default=dict)
    eco_score = models.IntegerField(default=0)
    selected_materials = models.JSONField(default=dict)
    total_area_sqm = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} — {self.bedrooms}BR {self.style} ({self.climate_zone})'
