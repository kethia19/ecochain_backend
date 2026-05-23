from django.contrib import admin
from .models import ClimateZone, EcoMaterial, Layout


@admin.register(ClimateZone)
class ClimateZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'cooling_strategy')
    search_fields = ('name', 'code')


@admin.register(EcoMaterial)
class EcoMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'element_type', 'carbon_score', 'cost_delta_pct', 'is_eco_alternative')
    list_filter = ('element_type', 'is_eco_alternative')
    search_fields = ('name',)


@admin.register(Layout)
class LayoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'bedrooms', 'climate_zone', 'style', 'eco_score', 'created_at')
    list_filter = ('climate_zone', 'style')
    search_fields = ('user__email',)
    readonly_fields = ('id', 'created_at', 'updated_at')
