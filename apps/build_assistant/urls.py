from django.urls import path
from .views import LayoutDetailView, ClimateZonesView, GenerateImagesView

urlpatterns = [
    path('layouts/<uuid:layout_id>', LayoutDetailView.as_view(),     name='layout-detail'),
    path('climate-zones',            ClimateZonesView.as_view(),      name='climate-zones'),
    path('layout/generate-images',   GenerateImagesView.as_view(),    name='layout-generate-images'),
]
