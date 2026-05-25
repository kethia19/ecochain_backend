"""
EcoChain Housing — AI Engine URLs
===================================
Team:    AI/ML (Group 15)
File:    apps/ai_engine/urls.py

Backend team — include this in eco_chain/urls.py:
    path('api/v1/', include('apps.ai_engine.urls')),
"""

from django.urls import path
from .views import (
    GreenMatchView,
    GreenMatchStatusView,
    LayoutGenerateView,
    MaterialSuggestView,
    TCOProjectionView,
    StandaloneEstimateView,
)

urlpatterns = [
    # Green Match — ML plant prediction
    # path("green-match/",        GreenMatchView.as_view(),       name="ai-green-match"),
    # path("green-match/status/", GreenMatchStatusView.as_view(), name="ai-green-match-status"),

    # Build Assistant — AI layout + materials
    path("layout/generate",     LayoutGenerateView.as_view(),   name="ai-layout-generate"),
    path("materials/suggest",   MaterialSuggestView.as_view(),  name="ai-materials-suggest"),

    # Cost Estimator — standalone form-driven estimate (no layout_id needed)
    # path("cost/estimate",       StandaloneEstimateView.as_view(), name="ai-cost-estimate"),
    path("cost/estimate-form/", StandaloneEstimateView.as_view(), name="ai-cost-estimate-form"),
    
    # Cost Estimator — AI 5-year savings projection (after layout generation)
    path("cost/tco-projection", TCOProjectionView.as_view(),    name="ai-tco-projection"),
]
