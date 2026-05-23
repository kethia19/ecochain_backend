from django.contrib import admin
from .models import MaterialPrice, LabourRate, CostEstimate, TCOProjection


@admin.register(MaterialPrice)
class MaterialPriceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'country', 'city', 'price_per_unit', 'currency', 'is_eco', 'last_updated')
    list_filter = ('country', 'category', 'is_eco')
    search_fields = ('name', 'city')


@admin.register(LabourRate)
class LabourRateAdmin(admin.ModelAdmin):
    list_display = ('skill_type', 'country', 'city', 'rate_per_day', 'currency', 'last_updated')
    list_filter = ('country', 'skill_type')
    search_fields = ('city',)


@admin.register(CostEstimate)
class CostEstimateAdmin(admin.ModelAdmin):
    list_display = ('user', 'layout_id', 'country', 'total_cost', 'currency', 'created_at')
    list_filter = ('country',)
    readonly_fields = ('id', 'created_at')


@admin.register(TCOProjection)
class TCOProjectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'layout_id', 'upfront_cost', 'total_savings', 'payback_months', 'created_at')
    readonly_fields = ('id', 'created_at')
