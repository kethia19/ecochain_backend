from django.contrib import admin
from .models import User, OTPVerification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('email', 'name')


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'used', 'expires_at', 'created_at')
    list_filter = ('used',)
    search_fields = ('user__email',)
