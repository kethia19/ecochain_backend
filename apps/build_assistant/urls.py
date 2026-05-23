from django.urls import path
from .views import GenerateLayoutView, SuggestMaterialsView, LayoutDetailView, ClimateZonesView

urlpatterns = [
    path('layout/generate', GenerateLayoutView.as_view(), name='layout-generate'),
    path('materials/suggest', SuggestMaterialsView.as_view(), name='materials-suggest'),
    path('layouts/<uuid:layout_id>', LayoutDetailView.as_view(), name='layout-detail'),
    path('climate-zones', ClimateZonesView.as_view(), name='climate-zones'),
]
