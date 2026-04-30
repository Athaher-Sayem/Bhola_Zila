# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import User, Profile, PreAdmin

# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.get_or_create(user=instance)
#     # Check if matches pre-admin table
#     try:
#         pre = PreAdmin.objects.get(email=instance.email)
#         if instance.role != 'admin' and instance.role != 'second_admin':
#             if instance.name.strip().lower() == pre.name.strip().lower():
#                 User.objects.filter(pk=instance.pk).update(role='second_admin', is_verified=True)
#                 Profile.objects.filter(user=instance).update(designation=pre.designation)
#     except PreAdmin.DoesNotExist:
#         pass

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from django.conf import settings
# from .models import User, Profile, PreAdmin

# @receiver(post_save, sender=User)
# def handle_user_post_save(sender, instance, created, **kwargs):

#     if created:
#         Profile.objects.get_or_create(user=instance)

#         send_mail(
#             "Welcome to BHOLA",
#             "Your account has been created successfully.",
#             settings.DEFAULT_FROM_EMAIL,
#             [instance.email],
#             fail_silently=False
#         )

#     pre = PreAdmin.objects.filter(email=instance.email).first()

#     if pre and instance.role not in ['admin', 'second_admin']:
#         if instance.name.strip().lower() == pre.name.strip().lower():

#             instance.role = 'second_admin'
#             instance.is_verified = True
#             instance.save(update_fields=['role', 'is_verified'])

#             Profile.objects.filter(user=instance).update(
#                 designation=pre.designation
#             )
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import User, Profile, PreAdmin


@receiver(post_save, sender=User)
def handle_user_post_save(sender, instance, created, **kwargs):

    # ---------------- USER CREATED ----------------
    if created:
        Profile.objects.get_or_create(user=instance)

    # ---------------- PREADMIN CHECK ----------------
    pre = PreAdmin.objects.filter(email=instance.email).first()

    if pre and instance.role not in ['admin', 'second_admin']:
        if instance.name.strip().lower() == pre.name.strip().lower():

            User.objects.filter(pk=instance.pk).update(
                role='second_admin',
                is_verified=True,
                account_approved=True,
            )

            Profile.objects.filter(user=instance).update(
                designation=pre.designation
            )