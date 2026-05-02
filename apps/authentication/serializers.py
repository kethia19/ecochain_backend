"""
Authentication serializers.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import User


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password],
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'location']
        extra_kwargs = {
            'name': {'required': True},
            'email': {'required': True},
            'location': {'required': False, 'allow_blank': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value.lower()

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, style={'input_type': 'password'},
    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'location', 'status', 'created_at']
        read_only_fields = fields


class AuthResponseSerializer(serializers.Serializer):
    """Documentation-only serializer for the login/verify response shape."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
