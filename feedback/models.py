from django.db import models
import uuid

STATUS_CHOICES = [
    ('open',     'Open'),
    ('reviewed', 'Reviewed'),
    ('resolved', 'Resolved'),
]

class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # anonymous — no FK to user; submitter_name is optional label only
    submitter_name = models.CharField(max_length=100, blank=True, help_text='Optional. Leave blank for anonymous.')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    admin_response = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'[{self.status}] {self.subject}'