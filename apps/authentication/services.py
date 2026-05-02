"""
Authentication services — encapsulates side effects (email sending, OTP creation).
"""
from django.core.mail import send_mail
from django.conf import settings

from .models import OTPVerification, User


def send_otp_email(user: User) -> OTPVerification:
    """Create a fresh OTP and email it to the user.

    In dev (no SENDGRID_API_KEY) this prints to the console so you can grab
    the code without a real inbox.
    """
    otp = OTPVerification.objects.create(user=user)

    subject = 'Your Eco-Chain verification code'
    message = (
        f'Hi {user.name},\n\n'
        f'Your Eco-Chain verification code is: {otp.otp_code}\n\n'
        f'This code expires in 15 minutes.\n\n'
        f'— The Eco-Chain Team'
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return otp
