"""
Plants models.

The `Plant` table is the master catalogue used by Green Match.
`UserPlant` links a user to plants they've added to their virtual garden.
`CareTask` represents upcoming reminders rendered on the dashboard.
"""
import uuid
from django.db import models
from django.conf import settings


class Plant(models.Model):
    """Master plant catalogue — the source of Green Match results."""

    class WaterLevel(models.TextChoices):
        MODERATE = 'moderate', 'Moderate'
        LOW = 'low', 'Low'
        ULTRA_LOW = 'ultra_low', 'Ultra-low'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=150)

    # We use JSONField (instead of ArrayField) so the project also runs on SQLite for dev.
    climate_zones = models.JSONField(default=list)
    sun_exposure = models.JSONField(default=list)
    soil_types = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    care_tips = models.JSONField(default=list)

    water_conservation = models.CharField(
        max_length=20, choices=WaterLevel.choices, default=WaterLevel.MODERATE,
    )
    water_frequency = models.CharField(max_length=100, blank=True)
    impact_label = models.CharField(max_length=50, blank=True)
    image_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserPlant(models.Model):
    """A plant the user has added to their personal garden."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='plants',
    )
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user.email} → {self.plant.name}'


class CareTask(models.Model):
    """A reminder for the user to do something to one of their plants."""

    class TaskType(models.TextChoices):
        WATER = 'water', 'Water'
        PRUNE = 'prune', 'Prune'
        FERTILIZE = 'fertilize', 'Fertilize'
        REPOT = 'repot', 'Repot'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='care_tasks',
    )
    user_plant = models.ForeignKey(
        UserPlant, on_delete=models.CASCADE, related_name='care_tasks', null=True, blank=True,
    )
    task_type = models.CharField(max_length=20, choices=TaskType.choices)
    description = models.CharField(max_length=255, blank=True)
    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f'{self.task_type} @ {self.due_date:%Y-%m-%d} ({self.user.email})'
