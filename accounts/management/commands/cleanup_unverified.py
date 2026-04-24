from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User, VERIFICATION_EXPIRY_HOURS


class Command(BaseCommand):
    help = (
        f'Delete user accounts that were never email-verified within the '
        f'{VERIFICATION_EXPIRY_HOURS}-hour window. '
        'Run this periodically (e.g. via a cron job or Celery beat).'
    )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(hours=VERIFICATION_EXPIRY_HOURS)
        expired_qs = User.objects.filter(
            is_email_verified=False,
            verification_token_created_at__lt=cutoff,
        )
        count = expired_qs.count()
        expired_qs.delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {count} expired unverified account(s).')
        )
