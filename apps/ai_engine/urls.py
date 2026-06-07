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
    MaintenanceInsightsView,
    ContentRecommendView,
    HouseGenerateView,
)

urlpatterns = [
    # Green Match — ML plant prediction (commented out; apps.green_match serves this path)
    # path("green-match/",        GreenMatchView.as_view(),       name="ai-green-match"),
    # path("green-match/status/", GreenMatchStatusView.as_view(), name="ai-green-match-status"),

    # Build Assistant — AI layout + materials
    path("layout/generate",     LayoutGenerateView.as_view(),   name="ai-layout-generate"),
    path("materials/suggest",   MaterialSuggestView.as_view(),  name="ai-materials-suggest"),

    # Cost Estimator — standalone form-driven estimate (no layout_id needed)
    path("cost/estimate-form/", StandaloneEstimateView.as_view(), name="ai-cost-estimate-form"),

    # Cost Estimator — AI 5-year savings projection (persists TCOProjection)
    path("cost/tco-projection", TCOProjectionView.as_view(),    name="ai-tco-projection"),

    # Maintenance — analytics from the maintenance dataset
    path("maintenance/insights",      MaintenanceInsightsView.as_view(), name="ai-maintenance-insights"),

    # Education Hub — personalised content recommendations
    path("education/recommendations", ContentRecommendView.as_view(),   name="ai-education-recommend"),

    # House Generation — AI design + Pollinations images + cost breakdown
    path("house/generate",            HouseGenerateView.as_view(),      name="ai-house-generate"),
]
