from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.core.files.base import ContentFile
from .models import User, Profile, PreAdmin
from .forms import SignupForm, LoginForm, ProfileForm
import io, os


def compress_profile_photo(upload_file):
    try:
        from PIL import Image as PILImage
        upload_file.seek(0)
        img = PILImage.open(upload_file)
        img.load()
        if img.mode not in ('RGB',):
            img = img.convert('RGB')
        img.thumbnail((600, 600), PILImage.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=82, optimize=True)
        buf.seek(0)
        stem = os.path.splitext(os.path.basename(upload_file.name))[0]
        return ContentFile(buf.read(), name=f'{stem}.jpg')
    except Exception:
        upload_file.seek(0)
        return upload_file


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_email_verified = False
            user.save()
            token = user.email_verification_token
            verify_url = request.build_absolute_uri(
                reverse('accounts:verify_email', args=[str(token)])
            )
            try:
                send_mail(
                    'Verify your DIU BZSF account',
                    f'Hi {user.name},\n\nClick the link to verify your email:\n{verify_url}\n\nDIU BZSF Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Account created! Please check your email to verify.')
            except Exception:
                messages.warning(request, 'Account created! (Check console for verification link in dev mode.)')
            return redirect('accounts:login')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
        user.is_email_verified = True
        user.save()
        messages.success(request, 'Email verified! You can now log in.')
    except User.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
    return redirect('accounts:login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_email_verified:
                messages.error(request, 'Please verify your email first.')
                return redirect('accounts:login')
            login(request, user)
            return redirect(request.GET.get('next', 'core:home'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('core:home')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            # Compress profile photo if new one uploaded
            if 'photo' in request.FILES:
                p.photo = compress_profile_photo(request.FILES['photo'])
            p.pending_verification = True
            p.save()
            messages.success(request, 'Profile updated! Awaiting verification.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def team_view(request):
    search = request.GET.get('q', '')
    designation = request.GET.get('designation', '')
    members = User.objects.filter(is_verified=True, is_email_verified=True).select_related('profile')
    if search:
        members = members.filter(name__icontains=search)
    if designation:
        members = members.filter(profile__designation__icontains=designation)
    designations = Profile.objects.values_list('designation', flat=True).distinct().exclude(designation='')
    return render(request, 'accounts/team.html', {'members': members, 'designations': designations})


@login_required
def verify_members(request):
    if not (request.user.is_admin or request.user.is_second_admin):
        messages.error(request, 'Permission denied.')
        return redirect('core:home')
    pending = User.objects.filter(profile__pending_verification=True).select_related('profile')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, pk=user_id)
        if action == 'verify':
            user.is_verified = True
            user.profile.pending_verification = False
            user.profile.save()
            user.save()
            messages.success(request, f'{user.name} has been verified.')
        elif action == 'reject':
            user.profile.pending_verification = False
            user.profile.save()
            messages.info(request, f'{user.name} was not verified.')
        return redirect('accounts:verify_members')
    return render(request, 'accounts/verify_members.html', {'pending': pending})
