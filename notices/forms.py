from django import forms
from .models import Notice, AUDIENCE_CHOICES

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'description', 'email_audience']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Notice Title'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Notice content...'}),
            'email_audience': forms.Select(),
        }
        labels = {
            'email_audience': 'Send email notification to',
        }