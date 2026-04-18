from django import forms
from .models import Event


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        # Return ALL files, not just the last one
        return files.getlist(name)


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'accept': 'image/*'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # data is now a list; validate each file individually
        if not data:
            if self.required:
                raise forms.ValidationError(self.error_messages['required'])
            return []
        result = []
        for f in data:
            result.append(super().clean(f, initial))
        return result


class EventForm(forms.ModelForm):
    images = MultipleFileField(
        required=False,
        label='Event Photos (max 5, each ≤ 10MB)'
    )

    class Meta:
        model = Event
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Event Title'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Event description...'}),
        }

    def clean_images(self):
        files = self.cleaned_data.get('images') or []
        if len(files) > 5:
            raise forms.ValidationError('Maximum 5 images allowed.')
        for f in files:
            if f.size > 10 * 1024 * 1024:
                raise forms.ValidationError(f'{f.name} exceeds 10MB limit.')
        return files