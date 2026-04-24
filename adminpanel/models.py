from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create',   'Created'),
        ('edit',     'Edited'),
        ('delete',   'Deleted'),
        ('verify',   'Verified'),
        ('login',    'Login'),
        ('logout',   'Logout'),
        ('register', 'Registered'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='activity_logs',
    )
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=50)
    target_id   = models.CharField(max_length=100, blank=True)
    target_name = models.CharField(max_length=255, blank=True)
    details     = models.TextField(blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        actor = self.user.name if self.user else "System"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {actor} {self.action}"