from django import forms
from .models import Task
from accounts.models import User

class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_email_verified=True, is_active=True).order_by('name'),
        label='Assign To',
        widget=forms.Select(),
    )
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Task title'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Task details...'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class TaskStatusForm(forms.Form):
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('in_progress', 'In Progress'),
        ('done',        'Done'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select())