# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth import login, logout
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.core.mail import send_mail
# from django.conf import settings
# from django.urls import reverse
# from django.core.files.base import ContentFile
# from .models import User, Profile, PreAdmin
# from .forms import (SignupForm, LoginForm, ProfileForm,
#                     ChangePasswordForm, ForgotPasswordForm,
#                     PasswordResetConfirmForm)
# from django.contrib.auth import update_session_auth_hash
# import io, os
# from django.utils import timezone
# from datetime import timedelta
# from django.shortcuts import get_object_or_404, redirect
# from django.http import HttpResponse
# from .models import User
# import uuid



# def _log(user, action, target_type, target_id, target_name, request, details=""):
#     try:
#         from adminpanel.models import ActivityLog
#         ActivityLog.objects.create(
#             user=user, action=action,
#             target_type=target_type, target_id=str(target_id),
#             target_name=target_name, details=details,
#             ip_address=request.META.get('REMOTE_ADDR'),
#         )
#     except Exception:
#         pass  # Never crash the real request


# def compress_profile_photo(upload_file):
#     try:
#         from PIL import Image as PILImage
#         upload_file.seek(0)
#         img = PILImage.open(upload_file)
#         img.load()
#         if img.mode not in ('RGB',):
#             img = img.convert('RGB')
#         img.thumbnail((600, 600), PILImage.LANCZOS)
#         buf = io.BytesIO()
#         img.save(buf, format='JPEG', quality=82, optimize=True)
#         buf.seek(0)
#         stem = os.path.splitext(os.path.basename(upload_file.name))[0]
#         return ContentFile(buf.read(), name=f'{stem}.jpg')
#     except Exception:
#         upload_file.seek(0)
#         return upload_file


# # def signup_view(request):
# #     if request.user.is_authenticated:
# #         return redirect('core:home')
# #     if request.method == 'POST':
# #         form = SignupForm(request.POST)
# #         if form.is_valid():
# #             user = form.save(commit=False)
# #             user.is_email_verified = False
# #             user.save()
# #             token = user.email_verification_token
# #             verify_url = request.build_absolute_uri(
# #                 reverse('accounts:verify_email', args=[str(token)])
# #             )
# #             try:
# #                 send_mail(
# #                     'Verify your DIU BZSF account',
# #                     f'Hi {user.name},\n\nClick the link to verify your email:\n{verify_url}\n\nDIU BZSF Team',
# #                     settings.DEFAULT_FROM_EMAIL,
# #                     [user.email],
# #                     fail_silently=False,
# #                 )
# #                 messages.success(request, 'Account created! Please check your email to verify.')
# #             except Exception:
# #                 messages.warning(request, 'Account created! (Check console for verification link in dev mode.)')
# #             return redirect('accounts:login')
# #     else:
# #         form = SignupForm()
# #     return render(request, 'accounts/signup.html', {'form': form})
# def signup_view(request):
#     if request.user.is_authenticated:
#         return redirect('core:home')

#     if request.method == 'POST':
#         form = SignupForm(request.POST)

#         if form.is_valid():
#             user = form.save(commit=False)

#             user.is_email_verified = False
#             user.email_verification_token = uuid.uuid4()
#             user.token_created_at = timezone.now()
#             user.save()

#             verify_url = request.build_absolute_uri(
#                 reverse('accounts:verify_email', args=[str(user.email_verification_token)])
#             )

#             send_mail(
#                 "Verify your BHOLA account 🎉",
#                 f"""
# Hi {user.name},

# Welcome to BHOLA 🎉

# Please verify your email using the link below:

# {verify_url}

# ⚠ This link is valid for 5 minutes only.

# If you did not create this account, ignore this email.

# — BHOLA Team
# """,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [user.email],
#                 fail_silently=False,
#             )

#             messages.success(request, 'Account created! Please check your email to verify.')
#             return redirect('accounts:login')
#     else:
#         form = SignupForm()

#     return render(request, 'accounts/signup.html', {'form': form})


# # def verify_email(request, token):
# #     user = get_object_or_404(User, email_verification_token=token)

# #     if user.token_created_at is None:
# #         messages.error(request, 'Invalid or expired verification link.')
# #         return redirect('accounts:login')

# #     if timezone.now() > user.token_created_at + timedelta(minutes=5):
# #         messages.error(request, 'Verification link expired. Please sign up again.')
# #         return redirect('accounts:login')

# #     user.is_email_verified = True
# #     user.email_verification_token = None
# #     user.token_created_at = None
# #     user.save(update_fields=['is_email_verified', 'email_verification_token', 'token_created_at'])

# #     messages.success(request, 'Email verified! You can now log in.')
# #     return redirect('accounts:login')

# def verify_email(request, token):
#     try:
#         user = User.objects.get(email_verification_token=token)
#     except User.DoesNotExist:
#         messages.error(request, 'Invalid or already-used link.')
#         return redirect('accounts:login')

#     if user.is_email_verified:
#         messages.info(request, 'Email already verified.')
#         return redirect('accounts:login')

#     if user.verification_expired:
#         user.delete()   # remove expired account
#         messages.error(request,
#             'Link expired (24h). Account removed — please register again.')
#         return redirect('accounts:signup')

#     user.is_email_verified = True
#     user.save(update_fields=['is_email_verified'])
#     messages.success(request, 'Email verified! You can now log in.')
#     return redirect('accounts:login')

# # def verify_email(request, token):
# #     try:
# #         user = User.objects.get(email_verification_token=token)
# #         user.is_email_verified = True
# #         user.save()
# #         messages.success(request, 'Email verified! You can now log in.')
# #     except User.DoesNotExist:
# #         messages.error(request, 'Invalid or expired verification link.')
# #     return redirect('accounts:login')
# # def verify_email(request, token):

# #     try:
# #         user = get_object_or_404(User, email_verification_token=token)

# #         # ---------------- EXPIRY CHECK (5 MINUTES) ----------------
# #         if user.token_created_at is None or timezone.now() > user.token_created_at + timedelta(minutes=5):
# #             messages.error(request, "Verification link expired. Please register again.")
# #             return redirect("accounts:login")

# #         # ---------------- VERIFY USER ----------------
# #         user.is_email_verified = True
# #         user.email_verification_token = None

# #         user.save(update_fields=['is_email_verified', 'email_verification_token'])

# #         messages.success(request, "Email verified successfully! You can now log in.")

# #     except User.DoesNotExist:
# #         messages.error(request, "Invalid verification link.")

# #     return redirect("accounts:login")

# def login_view(request):
#     if request.user.is_authenticated:
#         return redirect('core:home')
#     if request.method == 'POST':
#         form = LoginForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             if not user.is_email_verified:
#                 if user.verification_expired:
#                     user.delete()
#                     messages.error(request, 'Account removed (email not verified in 24h). Please register again.')
#                 else:
#                      messages.error(request, 'Please verify your email. Check your inbox.')
#                 return redirect('accounts:login')
#             login(request, user)
#             _log(user, 'login', 'session', '', user.name, request)
#             return redirect(request.GET.get('next', 'core:home'))
#     else:
#         form = LoginForm()
#     return render(request, 'accounts/login.html', {'form': form})


# def logout_view(request):
#     if request.user.is_authenticated:
#       _log(request.user, 'logout', 'session', '', request.user.name, request)
#     logout(request)
#     return redirect('core:home')


# @login_required
# def profile_view(request):
#     profile, _ = Profile.objects.get_or_create(user=request.user)
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             p = form.save(commit=False)
#             # Compress profile photo if new one uploaded
#             if 'photo' in request.FILES:
#                 p.photo = compress_profile_photo(request.FILES['photo'])
#             p.pending_verification = True
#             p.save()
#             messages.success(request, 'Profile updated! Awaiting verification.')
#             return redirect('accounts:profile')
#     else:
#         form = ProfileForm(instance=profile)
#     return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


# @login_required
# def team_view(request):
#     search = request.GET.get('q', '')
#     designation = request.GET.get('designation', '')
#     members = User.objects.filter(is_verified=True, is_email_verified=True).select_related('profile')
#     if search:
#         members = members.filter(name__icontains=search)
#     if designation:
#         members = members.filter(profile__designation__icontains=designation)
#     designations = Profile.objects.values_list('designation', flat=True).distinct().exclude(designation='')
#     return render(request, 'accounts/team.html', {'members': members, 'designations': designations})


# @login_required
# def verify_members(request):
#     if not (request.user.is_admin or request.user.is_second_admin):
#         messages.error(request, 'Permission denied.')
#         return redirect('core:home')
#     pending = User.objects.filter(profile__pending_verification=True).select_related('profile')
#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')
#         action = request.POST.get('action')
#         user = get_object_or_404(User, pk=user_id)
#         if action == 'verify':
#             user.is_verified = True
#             user.profile.pending_verification = False
#             user.profile.save()
#             user.save()
#             messages.success(request, f'{user.name} has been verified.')
#         elif action == 'reject':
#             user.profile.pending_verification = False
#             user.profile.save()
#             messages.info(request, f'{user.name} was not verified.')
#         return redirect('accounts:verify_members')
#     return render(request, 'accounts/verify_members.html', {'pending': pending})



# @login_required
# def change_password(request):
#     if request.method == 'POST':
#         form = ChangePasswordForm(request.user, request.POST)
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)
#             _log_action(request.user, 'edit', 'password', str(request.user.pk), request.user.name, request)
#             messages.success(request, 'Password updated successfully.')
#             return redirect('accounts:profile')
#     else:
#         form = ChangePasswordForm(request.user)
#     return render(request, 'accounts/change_password.html', {'form': form})


# def forgot_password(request):
#     if request.user.is_authenticated:
#         return redirect('core:home')
#     if request.method == 'POST':
#         form = ForgotPasswordForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             try:
#                 user = User.objects.get(email=email, is_email_verified=True)
#                 user.generate_password_reset_token()
#                 reset_url = request.build_absolute_uri(
#                     reverse('accounts:password_reset_confirm', args=[str(user.password_reset_token)])
#                 )
#                 try:
#                     send_mail(
#                         'Reset your DIU BZSF password',
#                         f'Hi {user.name},\n\nReset your password here:\n{reset_url}\n\nThis link expires in 2 hours.\n\nDIU BZSF Team',
#                         settings.DEFAULT_FROM_EMAIL,
#                         [user.email],
#                         fail_silently=False,
#                     )
#                 except Exception:
#                     pass
#             except User.DoesNotExist:
#                 pass  # Silent — don't reveal whether email exists
#             messages.success(
#                 request,
#                 'If that email is registered, a reset link has been sent. Check your inbox (or console in dev mode).'
#             )
#             return redirect('accounts:login')
#     else:
#         form = ForgotPasswordForm()
#     return render(request, 'accounts/forgot_password.html', {'form': form})


# def password_reset_confirm(request, token):
#     try:
#         user = User.objects.get(password_reset_token=token)
#     except User.DoesNotExist:
#         messages.error(request, 'Invalid or expired password reset link.')
#         return redirect('accounts:forgot_password')

#     if user.password_reset_expired:
#         messages.error(request, 'This reset link has expired (2 h window). Please request a new one.')
#         return redirect('accounts:forgot_password')

#     if request.method == 'POST':
#         form = PasswordResetConfirmForm(request.POST)
#         if form.is_valid():
#             user.set_password(form.cleaned_data['password1'])
#             user.password_reset_token = None
#             user.password_reset_token_created_at = None
#             user.save()
#             messages.success(request, 'Password reset successfully! You can now log in.')
#             return redirect('accounts:login')
#     else:
#         form = PasswordResetConfirmForm()
#     return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'token': token})



# # ---- helper ----
# def _log_action(user, action, target_type, target_id, target_name, request, details=''):
#     """Create an ActivityLog entry (silently — never let logging break the request)."""
#     try:
#         from adminpanel.models import ActivityLog
#         ip = request.META.get('REMOTE_ADDR')
#         ActivityLog.objects.create(
#             user=user,
#             action=action,
#             target_type=target_type,
#             target_id=target_id,
#             target_name=target_name,
#             details=details,
#             ip_address=ip,
#         )
#     except Exception:
#         pass



# def resend_verification(request):
#     if request.user.is_authenticated:
#         return redirect('core:home')
#     if request.method == 'POST':
#         email = request.POST.get('email', '').strip()
#         try:
#             user = User.objects.get(email=email, is_email_verified=False)
#         except User.DoesNotExist:
#             messages.error(request, 'No unverified account with that email.')
#             return redirect('accounts:resend_verification')

#         if user.verification_expired:
#             user.delete()
#             messages.error(request, 'Account expired. Please register again.')
#             return redirect('accounts:signup')

#         user.regenerate_verification_token()
#         _send_verification_email(request, user)
#         messages.success(request, 'Verification email resent! Check your inbox.')
#         return redirect('accounts:login')
#     return render(request, 'accounts/resend_verification.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.core.files.base import ContentFile
from .models import User, Profile, PreAdmin
from .forms import SignupForm, LoginForm, ProfileForm, ChangePasswordForm, ForgotPasswordForm, PasswordResetConfirmForm
import io, os




# ---- helper ----
def _log_action(user, action, target_type, target_id, target_name, request, details=''):
    """Create an ActivityLog entry (silently — never let logging break the request)."""
    try:
        from adminpanel.models import ActivityLog
        ip = request.META.get('REMOTE_ADDR')
        ActivityLog.objects.create(
            user=user,
            action=action,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            details=details,
            ip_address=ip,
        )
    except Exception:
        pass



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


def _send_verification_email(request, user):
    verify_url = request.build_absolute_uri(
        reverse('accounts:verify_email', args=[str(user.email_verification_token)])
    )
    try:
        send_mail(
            'Verify your DIU BZSF account',
            f'Hi {user.name},\n\nClick the link to verify your email:\n{verify_url}\n\nThis link expires in 24 hours.\n\nDIU BZSF Team',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception:
        pass  # console backend will print it


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_email_verified = False
            user.save()
            _send_verification_email(request, user)
            messages.success(request, 'Account created! Check your email to verify.')
            return redirect('accounts:login')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
    except User.DoesNotExist:
        messages.error(request, 'Invalid or already-used verification link.')
        return redirect('accounts:login')

    if user.is_email_verified:
        messages.info(request, 'Email already verified. Please log in.')
        return redirect('accounts:login')

    if user.verification_expired:
        # Delete the stale account so the user can re-register
        user.delete()
        messages.error(
            request,
            'This verification link has expired (24 h window). '
            'Your account has been removed — please register again.'
        )
        return redirect('accounts:signup')

    user.is_email_verified = True
    user.save(update_fields=['is_email_verified'])
    messages.success(request, 'Email verified! You can now log in.')
    return redirect('accounts:login')


def resend_verification(request):
    """Let a user resend their verification email (before the 24 h window closes)."""
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email, is_email_verified=False)
        except User.DoesNotExist:
            messages.error(request, 'No unverified account found with that email.')
            return redirect('accounts:resend_verification')

        if user.verification_expired:
            user.delete()
            messages.error(
                request,
                'Your account had expired. Please register again.'
            )
            return redirect('accounts:signup')

        user.regenerate_verification_token()
        _send_verification_email(request, user)
        messages.success(request, 'Verification email resent! Check your inbox .')
        return redirect('accounts:login')
    return render(request, 'accounts/resend_verification.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_email_verified:
                if user.verification_expired:
                    user.delete()
                    messages.error(
                        request,
                        'Your account was removed because the email was never verified within 24 hours. '
                        'Please register again.'
                    )
                else:
                    messages.error(
                        request,
                        'Please verify your email first. '
                    )
                return redirect('accounts:login')
            login(request, user)
            # Log the login action
            _log_action(user, 'login', 'session', '', user.name, request)
            return redirect(request.GET.get('next', 'core:home'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        _log_action(request.user, 'logout', 'session', '', request.user.name, request)
    logout(request)
    return redirect('core:home')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            if 'photo' in request.FILES:
                p.photo = compress_profile_photo(request.FILES['photo'])
            p.pending_verification = True
            p.save()
            _log_action(request.user, 'edit', 'profile', str(request.user.pk), request.user.name, request)
            messages.success(request, 'Profile updated! Awaiting verification.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            _log_action(request.user, 'edit', 'password', str(request.user.pk), request.user.name, request)
            messages.success(request, 'Password updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


def forgot_password(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email, is_email_verified=True)
                user.generate_password_reset_token()
                reset_url = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', args=[str(user.password_reset_token)])
                )
                try:
                    send_mail(
                        'Reset your DIU BZSF password',
                        f'Hi {user.name},\n\nReset your password here:\n{reset_url}\n\nThis link expires in 2 hours.\n\nDIU BZSF Team',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                except Exception:
                    pass
            except User.DoesNotExist:
                pass  # Silent — don't reveal whether email exists
            messages.success(
                request,
                'If that email is registered, a reset link has been sent. Check your inbox .'
            )
            return redirect('accounts:login')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})


def password_reset_confirm(request, token):
    try:
        user = User.objects.get(password_reset_token=token)
    except User.DoesNotExist:
        messages.error(request, 'Invalid or expired password reset link.')
        return redirect('accounts:forgot_password')

    if user.password_reset_expired:
        messages.error(request, 'This reset link has expired (2 h window). Please request a new one.')
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.password_reset_token = None
            user.password_reset_token_created_at = None
            user.save()
            messages.success(request, 'Password reset successfully! You can now log in.')
            return redirect('accounts:login')
    else:
        form = PasswordResetConfirmForm()
    return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'token': token})


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
            _log_action(request.user, 'verify', 'user', str(user.pk), user.name, request)
            messages.success(request, f'{user.name} has been verified.')
        elif action == 'reject':
            user.profile.pending_verification = False
            user.profile.save()
            _log_action(request.user, 'edit', 'user', str(user.pk), user.name, request, details='Verification rejected')
            messages.info(request, f'{user.name} was not verified.')
        return redirect('accounts:verify_members')
    return render(request, 'accounts/verify_members.html', {'pending': pending})


