"""
eco_chain URL configuration.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # AI/ML endpoints — mounted first so they take priority over stub app views
    # at overlapping paths (green-match, layout/generate, materials/suggest,
    # cost/tco-projection). Non-overlapping app routes are unaffected.
    path("api/v1/", include("apps.ai_engine.urls")),

    # App endpoints
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
    path('api/v1/green-match/', include('apps.green_match.urls')),
    path('api/v1/', include('apps.plants.urls')),
    path('api/v1/', include('apps.build_assistant.urls')),
    path('api/v1/', include('apps.cost_estimator.urls')),
    path('api/v1/', include('apps.saved_recommendations.urls')),

    # OpenAPI schema + interactive docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
