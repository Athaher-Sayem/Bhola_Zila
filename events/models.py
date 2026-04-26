from django.db import models
from accounts.models import User
import uuid

def event_image_path(instance, filename):
    import os
    ext = os.path.splitext(filename)[1].lower() or '.jpg'
    return f'events/{instance.event_id}/{uuid.uuid4().hex}{ext}'
    

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=event_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)



class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('interested', 'Interested'),
        ('registered', 'Registered'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user  = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='event_registrations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-registered_at']

    def __str__(self):
        return f'{self.user.name} → {self.event.title}'