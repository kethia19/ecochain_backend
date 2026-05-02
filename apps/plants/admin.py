from django.contrib import admin
from .models import Plant, UserPlant, CareTask


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'scientific_name', 'water_conservation')
    search_fields = ('name', 'scientific_name')


@admin.register(UserPlant)
class UserPlantAdmin(admin.ModelAdmin):
    list_display = ('user', 'plant', 'added_at')


@admin.register(CareTask)
class CareTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task_type', 'due_date', 'completed')
    list_filter = ('task_type', 'completed')
