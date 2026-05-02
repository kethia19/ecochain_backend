"""
Authentication views.
"""
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTRefreshView

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from django.contrib.auth import authenticate

from .models import User, OTPVerification
from .serializers import (
    SignUpSerializer,
    VerifyOTPSerializer,
    ResendOTPSerializer,
    LoginSerializer,
    UserSerializer,
    AuthResponseSerializer,
)
from .services import send_otp_email


# ---------- helpers ----------------------------------------------------------

LOGIN_FAIL_LIMIT = 10
LOGIN_LOCK_SECONDS = 60 * 30  # 30 minutes


def _login_lock_key(email: str) -> str:
    return f'login_fail:{email.lower()}'


def _is_locked(email: str) -> bool:
    return (cache.get(_login_lock_key(email)) or 0) >= LOGIN_FAIL_LIMIT


def _record_failure(email: str) -> None:
    key = _login_lock_key(email)
    fails = (cache.get(key) or 0) + 1
    cache.set(key, fails, timeout=LOGIN_LOCK_SECONDS)


def _clear_failures(email: str) -> None:
    cache.delete(_login_lock_key(email))


def _issue_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    }


# ---------- views ------------------------------------------------------------

class SignUpView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        summary='Register a new user',
        request=SignUpSerializer,
        responses={
            201: OpenApiResponse(description='Account created. OTP emailed.'),
            400: OpenApiResponse(description='Validation error.'),
        },
        examples=[
            OpenApiExample(
                'Sign-up payload',
                value={
                    'name': 'Amara Okafor',
                    'email': 'amara@example.com',
                    'password': 'StrongPass!23',
                    'location': 'Lagos, Nigeria',
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_otp_email(user)
        return Response(
            {'detail': 'Account created. Check your email for your OTP.'},
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        summary='Verify a user via 6-digit OTP',
        request=VerifyOTPSerializer,
        responses={
            200: AuthResponseSerializer,
            400: OpenApiResponse(description='Invalid OTP.'),
            409: OpenApiResponse(description='Account already verified.'),
            410: OpenApiResponse(description='OTP expired.'),
        },
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp']

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid OTP.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if user.status == User.Status.ACTIVE:
            return Response({'detail': 'Account already verified.'},
                            status=status.HTTP_409_CONFLICT)

        otp = user.otps.filter(otp_code=otp_code, used=False).order_by('-expires_at').first()
        if otp is None:
            return Response({'detail': 'Invalid OTP.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not otp.is_valid():
            return Response(
                {'detail': 'OTP expired. Request a new one.'},
                status=status.HTTP_410_GONE,
            )

        otp.used = True
        otp.save(update_fields=['used'])

        user.status = User.Status.ACTIVE
        user.save(update_fields=['status'])

        return Response(_issue_tokens(user), status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        summary='Resend a verification OTP',
        request=ResendOTPSerializer,
        responses={200: OpenApiResponse(description='OTP resent (if account exists).')},
    )
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Always return 200 to avoid leaking whether the account exists.
        try:
            user = User.objects.get(email__iexact=email)
            if user.status == User.Status.UNVERIFIED:
                send_otp_email(user)
        except User.DoesNotExist:
            pass

        return Response(
            {'detail': 'If that email exists and is unverified, a new OTP has been sent.'},
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        summary='Log in with email and password',
        request=LoginSerializer,
        responses={
            200: AuthResponseSerializer,
            401: OpenApiResponse(description='Invalid credentials.'),
            403: OpenApiResponse(description='Account not verified or suspended.'),
            429: OpenApiResponse(description='Too many failed attempts — try again later.'),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        if _is_locked(email):
            return Response(
                {'detail': 'Account temporarily locked due to too many failed attempts.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = authenticate(request, username=email, password=password)
        if user is None:
            _record_failure(email)
            return Response({'detail': 'Invalid credentials.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if user.status != User.Status.ACTIVE:
            return Response(
                {'detail': 'Account not verified or suspended.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        _clear_failures(email)
        return Response(_issue_tokens(user), status=status.HTTP_200_OK)


class TokenRefreshView(SimpleJWTRefreshView):
    """Thin wrapper so the endpoint shows up in the Swagger schema with a tag."""

    @extend_schema(
        tags=['Authentication'],
        summary='Refresh an access token',
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
