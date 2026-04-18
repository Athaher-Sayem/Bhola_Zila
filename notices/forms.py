from django import forms
from .models import Notice

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Notice Title'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Notice content...'}),
        }
