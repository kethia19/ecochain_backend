"""
Plants URLs — mounted at /api/v1/.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('plants/<uuid:id>/', views.PlantDetailView.as_view(), name='plant-detail'),
    path('user/plants/', views.AddUserPlantView.as_view(), name='user-plants'),
]
