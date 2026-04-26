from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'message', 'submitter_name']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Brief subject of your feedback or complaint'}),
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe your issue or feedback...'}),
            'submitter_name': forms.TextInput(attrs={'placeholder': 'Your name (optional — leave blank for anonymous)'}),
        }
        labels = {
            'submitter_name': 'Your name (optional)',
        }

class FeedbackResponseForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['status', 'admin_response']
        widgets = {
            'admin_response': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your response to this submission...'}),
        }
        labels = {
            'status': 'Update Status',
            'admin_response': 'Admin Response',
        }