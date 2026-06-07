from django.urls import path
from .views import (
    EstimateCostView,
    PricingMaterialsView,
    PricingLabourView,
    CostReportView,
)

urlpatterns = [
    path('cost/estimate',                   EstimateCostView.as_view(),      name='cost-estimate'),
    path('pricing/materials',               PricingMaterialsView.as_view(),  name='pricing-materials'),
    path('pricing/labour',                  PricingLabourView.as_view(),     name='pricing-labour'),
    path('cost/report/<uuid:layout_id>',    CostReportView.as_view(),        name='cost-report'),
]
