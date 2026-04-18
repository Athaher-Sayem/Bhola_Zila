from django import forms
from .models import Event

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class EventForm(forms.ModelForm):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={'accept': 'image/*'}),
        required=False, label='Event Photos (max 5, each ≤ 10MB)'
    )

    class Meta:
        model = Event
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Event Title'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Event description...'}),
        }

    def clean_images(self):
        files = self.files.getlist('images')
        if len(files) > 5:
            raise forms.ValidationError('Maximum 5 images allowed.')
        for f in files:
            if f.size > 10 * 1024 * 1024:
                raise forms.ValidationError(f'{f.name} exceeds 10MB limit.')
        return files
