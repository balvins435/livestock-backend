from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_verification_email(user, token):
    """Send email verification"""
    
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
    
    subject = 'Verify Your LiveStock Sentinel Account'
    message = f'''
Hi {user.first_name},

Welcome to LiveStock Sentinel!

Please verify your email address by clicking the link below:
{verification_url}

This link expires in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
LiveStock Sentinel Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_password_reset_email(user, token):
    """Send password reset email"""
    
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
    
    subject = 'Reset Your Password - LiveStock Sentinel'
    message = f'''
Hi {user.first_name},

You requested to reset your password.

Click the link below to reset your password:
{reset_url}

This link expires in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
LiveStock Sentinel Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
