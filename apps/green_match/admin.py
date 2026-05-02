from django.contrib import admin
from .models import MatchSession


@admin.register(MatchSession)
class MatchSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'climate_zone', 'created_at')
    search_fields = ('user__email', 'location')
