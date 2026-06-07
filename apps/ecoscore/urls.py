from django.urls import path
from .views import EcoScoreCalculateView

urlpatterns = [
    path('ecoscore/calculate', EcoScoreCalculateView.as_view(), name='ecoscore-calculate'),
]
