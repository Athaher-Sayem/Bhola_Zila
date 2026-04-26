# bhola/email_utils.py
"""
Shared email utilities for BHOLA.
"""
from django.core.mail import send_mass_mail
from django.conf import settings
from accounts.models import User


def notify_all_users(subject: str, message: str, audience: str = 'all'):
    """
    Send an email to users based on audience.

    audience options:
        'all'            — every email-verified user
        'members'        — role == 'member' only
        'advisors'       — role == 'advisor' only
        'admins'         — role in ('admin', 'second_admin')
    """
    qs = User.objects.filter(is_email_verified=True, is_active=True)
    if audience == 'members':
        qs = qs.filter(role='member')
    elif audience == 'advisors':
        qs = qs.filter(role='advisor')
    elif audience == 'admins':
        qs = qs.filter(role__in=['admin', 'second_admin'])
    # 'all' → no extra filter

    recipients = list(qs.values_list('email', flat=True))
    if not recipients:
        return

    # send_mass_mail takes a tuple of (subject, body, from, [recipients])
    datatuple = tuple(
        (subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        for email in recipients
    )
    try:
        send_mass_mail(datatuple, fail_silently=True)
    except Exception:
        pass