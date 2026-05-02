from django.contrib import admin
from .models import ImpactLog


@admin.register(ImpactLog)
class ImpactLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'water_saved_litres', 'co2_offset_kg', 'created_at')
