from django.urls import path
from .views import (
    SavedRecommendationListCreateView,
    SavedRecommendationDetailView,
)

urlpatterns = [
    path(
        'saved-recommendations/',
        SavedRecommendationListCreateView.as_view(),
        name='saved-recommendations-list',
    ),
    path(
        'saved-recommendations/<uuid:recommendation_id>/',
        SavedRecommendationDetailView.as_view(),
        name='saved-recommendations-detail',
    ),
]