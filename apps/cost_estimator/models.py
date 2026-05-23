import uuid
from django.db import models
from django.conf import settings


COUNTRY_CHOICES = [
    ('NG', 'Nigeria'),
    ('KE', 'Kenya'),
    ('GH', 'Ghana'),
    ('ET', 'Ethiopia'),
    ('ZA', 'South Africa'),
    ('SN', 'Senegal'),
]

SKILL_CHOICES = [
    ('mason', 'Mason'),
    ('carpenter', 'Carpenter'),
    ('plumber', 'Plumber'),
    ('electrician', 'Electrician'),
    ('labourer', 'General Labourer'),
]

CATEGORY_CHOICES = [
    ('wall', 'Wall'),
    ('foundation', 'Foundation'),
    ('roof', 'Roof'),
    ('floor', 'Floor'),
    ('window', 'Window'),
    ('insulation', 'Insulation'),
    ('finishing', 'Finishing'),
]


class MaterialPrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    unit = models.CharField(max_length=30)
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    city = models.CharField(max_length=100, blank=True)
    carbon_score = models.FloatField(default=0.0)
    is_eco = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['country', 'category', 'name']
        indexes = [
            models.Index(fields=['country', 'category']),
            models.Index(fields=['country', 'city', 'category']),
        ]

    def __str__(self):
        return f'{self.name} ({self.country}, {self.currency} {self.price_per_unit}/{self.unit})'


class LabourRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    skill_type = models.CharField(max_length=50, choices=SKILL_CHOICES)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    city = models.CharField(max_length=100, blank=True)
    rate_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['country', 'skill_type']
        indexes = [
            models.Index(fields=['country', 'skill_type']),
        ]

    def __str__(self):
        return f'{self.skill_type} — {self.country} {self.currency} {self.rate_per_day}/day'


class CostEstimate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    layout_id = models.UUIDField(db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cost_estimates',
    )
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    city = models.CharField(max_length=100, blank=True)
    total_cost = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=5)
    breakdown = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} layout={self.layout_id} {self.currency} {self.total_cost}'


class TCOProjection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    layout_id = models.UUIDField(db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tco_projections',
    )
    upfront_cost = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=5)
    projection_years = models.IntegerField(default=5)
    annual_savings = models.DecimalField(max_digits=12, decimal_places=2)
    total_savings = models.DecimalField(max_digits=14, decimal_places=2)
    payback_months = models.IntegerField()
    savings_breakdown = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} layout={self.layout_id} payback={self.payback_months}mo'
