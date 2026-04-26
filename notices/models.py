from django.db import models
from accounts.models import User
import uuid

AUDIENCE_CHOICES = [
    ('all',      'All Users'),
    ('members',  'Members Only'),
    ('advisors', 'Advisors Only'),
    ('admins',   'Admins Only'),
]

class Notice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='notices')
    created_at = models.DateTimeField(auto_now_add=True)
    email_audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    

