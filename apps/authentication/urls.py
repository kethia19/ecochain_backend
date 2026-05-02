"""
Authentication URLs.
All paths are mounted under /api/v1/auth/ by the project urls.py.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('verify/', views.VerifyOTPView.as_view(), name='verify'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend-otp'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('refresh/', views.TokenRefreshView.as_view(), name='token-refresh'),
]
