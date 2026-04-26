from django.db import models
from accounts.models import User
import uuid

STATUS_CHOICES = [
    ('pending',     'Pending'),
    ('in_progress', 'In Progress'),
    ('done',        'Done'),
]

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['deadline', '-created_at']

    def __str__(self):
        return self.title

    def is_overdue(self):
        from django.utils import timezone
        if self.deadline and self.status != 'done':
            return timezone.now().date() > self.deadline
        return False