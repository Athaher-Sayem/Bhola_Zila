from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Profile
from django.contrib.auth import password_validation

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), label='Confirm Password')

    class Meta:
        model = User
        fields = ['name', 'email', 'student_id']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'student_id': forms.TextInput(attrs={'placeholder': 'Student ID'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            Profile.objects.get_or_create(user=user)
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}), label='Email')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'address', 'batch', 'designation', 'photo']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself...'}),
            'address': forms.TextInput(attrs={'placeholder': 'Your Address'}),
            'batch': forms.TextInput(attrs={'placeholder': 'e.g. 2021'}),
            'designation': forms.TextInput(attrs={'placeholder': 'e.g. President'}),
        }


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'}), label='Current Password')
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}), label='New Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}), label='Confirm')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        pwd = self.cleaned_data.get('current_password')
        if not self.user.check_password(pwd):
            raise forms.ValidationError('Current password is incorrect.')
        return pwd

    def clean(self):
        cleaned_data = super().clean()
        p1, p2 = cleaned_data.get('password1'), cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('New passwords do not match.')
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data['password1'])
        self.user.save()
        return self.user


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your email'}))


class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm'}))

    def clean(self):
        cleaned_data = super().clean()
        p1, p2 = cleaned_data.get('password1'), cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data