from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import password_validation
from .models import User, Profile, BLOOD_GROUPS




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
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'})
    )
    password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat new password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1, p2 = cleaned_data.get('password1'), cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data
    


class ProfileForm(forms.Form):
    """
    Standalone form — does NOT save directly to Profile.
    Data goes to PendingProfileChange for admin review instead.
    """
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself...'}),
        label='Bio'
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Your Address'}),
        label='Address'
    )
    batch = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. 2021'}),
        label='Batch'
    )
    designation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. President'}),
        label='Designation'
    )
    blood_group = forms.ChoiceField(
        choices=BLOOD_GROUPS,
        required=False,
        label='Blood Group'
    )
    photo = forms.ImageField(
        required=False,
        label='Profile Photo'
    )