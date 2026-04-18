from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile, PreAdmin

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
    # Check if matches pre-admin table
    try:
        pre = PreAdmin.objects.get(email=instance.email)
        if instance.role != 'admin' and instance.role != 'second_admin':
            if instance.name.strip().lower() == pre.name.strip().lower():
                User.objects.filter(pk=instance.pk).update(role='second_admin', is_verified=True)
                Profile.objects.filter(user=instance).update(designation=pre.designation)
    except PreAdmin.DoesNotExist:
        pass
