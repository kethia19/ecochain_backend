"""
Green Match URLs — mounted at /api/v1/green-match/.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.GreenMatchView.as_view(), name='green-match'),
]
