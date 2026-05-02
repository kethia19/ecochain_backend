"""
Dashboard URLs — mounted at /api/v1/dashboard/.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
]
