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
            user.account_approved = False
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

    # Notify all admins that a new user needs approval
    try:
        admin_emails = list(
            User.objects.filter(role__in=['admin', 'second_admin'], is_email_verified=True)
            .values_list('email', flat=True)
        )
        if admin_emails:
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                f'[BZSF] New member pending approval: {user.name}',
                f'A new user verified their email and needs account approval.\n\n'
                f'Name: {user.name}\nEmail: {user.email}\nStudent ID: {user.student_id}\n\n'
                f'Log in to the admin panel to approve or reject.',
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True,
            )
    except Exception:
        pass

    messages.success(
        request,
        'Email verified! Your account is pending admin approval. '
        'You will be notified once approved.'
    )
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
                    messages.error(request, 'Please verify your email first. Check your inbox.')
                return redirect('accounts:login')

            # Block rejected accounts
            if user.account_rejected:
                reason = user.rejection_reason or 'No reason provided.'
                messages.error(request, f'Your account application was rejected. Reason: {reason}')
                return redirect('accounts:login')

            login(request, user)
            _log_action(user, 'login', 'session', '', user.name, request)

            # Warn pending accounts (they can log in but with limited access)
            if not user.account_approved and not user.is_admin:
                messages.info(
                    request,
                    'You are logged in, but your account is pending admin approval. '
                    'Some features are restricted until approved.'
                )

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
    from .models import PendingProfileChange
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Check if there is already a pending change awaiting review
    pending_change = PendingProfileChange.objects.filter(
        user=request.user, status='pending'
    ).first()

    if request.method == 'POST':
        # Block re-submission while a change is already pending
        if pending_change:
            messages.warning(request, 'You already have a pending profile change awaiting admin review.')
            return redirect('accounts:profile')

        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            change = PendingProfileChange(user=request.user)

            # Only store fields that actually differ from the current profile
            if data.get('bio') != profile.bio:
                change.new_bio = data.get('bio', '')
            if data.get('address') != profile.address:
                change.new_address = data.get('address', '')
            if data.get('batch') != profile.batch:
                change.new_batch = data.get('batch', '')
            if data.get('designation') != profile.designation:
                change.new_designation = data.get('designation', '')
            if data.get('blood_group') != profile.blood_group:
                change.new_blood_group = data.get('blood_group', '')

            # Handle photo
            if 'photo' in request.FILES:
                compressed = compress_profile_photo(request.FILES['photo'])
                change.new_photo = compressed

            # Only save if something actually changed
            has_changes = any([
                change.new_bio is not None,
                change.new_address is not None,
                change.new_batch is not None,
                change.new_designation is not None,
                change.new_blood_group is not None,
                change.new_photo,
            ])

            if has_changes:
                change.save()
                _log_action(request.user, 'edit', 'profile_change', str(change.pk), request.user.name, request)
                messages.success(
                    request,
                    'Profile changes submitted for admin review. '
                    'They will appear on your profile once approved.'
                )
            else:
                messages.info(request, 'No changes detected.')

            return redirect('accounts:profile')
    else:
        # Pre-fill form with current profile values
        form = ProfileForm(initial={
            'bio': profile.bio,
            'address': profile.address,
            'batch': profile.batch,
            'designation': profile.designation,
            'blood_group': profile.blood_group,
        })

    # Get recent change history for display
    recent_changes = PendingProfileChange.objects.filter(
        user=request.user
    ).order_by('-submitted_at')[:5]

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
        'pending_change': pending_change,
        'recent_changes': recent_changes,
    })


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
    members = User.objects.filter(
        is_verified=True,
        is_email_verified=True,
        account_approved=True
    ).select_related('profile')
    if search:
        members = members.filter(name__icontains=search)
    if designation:
        members = members.filter(profile__designation__icontains=designation)
    designations = Profile.objects.values_list('designation', flat=True).distinct().exclude(designation='')
    return render(request, 'accounts/team.html', {'members': members, 'designations': designations})


@login_required
def verify_members(request):
    from .models import PendingProfileChange
    if not (request.user.is_admin or request.user.is_second_admin):
        messages.error(request, 'Permission denied.')
        return redirect('core:home')

    # Accounts that verified email but are not yet admin-approved
    pending_accounts = User.objects.filter(
        is_email_verified=True,
        account_approved=False,
        account_rejected=False
    ).select_related('profile').order_by('date_joined')

    # Profile changes awaiting review
    pending_profiles = PendingProfileChange.objects.filter(
        status='pending'
    ).select_related('user', 'user__profile').order_by('-submitted_at')

    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        if action_type == 'account':
            user_id = request.POST.get('user_id')
            action = request.POST.get('action')
            user = get_object_or_404(User, pk=user_id)

            if action == 'approve':
                user.account_approved = True
                user.is_verified = True
                user.account_rejected = False
                user.rejection_reason = ''
                user.save()
                _log_action(request.user, 'verify', 'user', str(user.pk), user.name, request)
                try:
                    send_mail(
                        '[BZSF] Your account has been approved!',
                        f'Hi {user.name},\n\nYour BZSF account has been approved. '
                        f'You now have full access.\n\nDIU BZSF Team',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
                messages.success(request, f'{user.name}\'s account has been approved.')

            elif action == 'reject':
                reason = request.POST.get('rejection_reason', '')
                user.account_rejected = True
                user.account_approved = False
                user.rejection_reason = reason
                user.save()
                _log_action(request.user, 'edit', 'user', str(user.pk), user.name, request, details=f'Rejected: {reason}')
                try:
                    send_mail(
                        '[BZSF] Account application update',
                        f'Hi {user.name},\n\nYour BZSF account was not approved.\n'
                        f'Reason: {reason or "No reason provided"}\n\nDIU BZSF Team',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
                messages.info(request, f'{user.name}\'s account was rejected.')

        elif action_type == 'profile':
            change_id = request.POST.get('change_id')
            action = request.POST.get('action')
            change = get_object_or_404(PendingProfileChange, pk=change_id)
            from django.utils import timezone as tz
            change.reviewed_by = request.user
            change.reviewed_at = tz.now()

            if action == 'approve':
                change.status = 'approved'
                change.save()
                change.apply_to_profile()
                _log_action(request.user, 'verify', 'profile', str(change.pk), change.user.name, request)
                try:
                    send_mail(
                        '[BZSF] Profile update approved',
                        f'Hi {change.user.name},\n\nYour profile update has been approved and is now live.\n\nDIU BZSF Team',
                        settings.DEFAULT_FROM_EMAIL,
                        [change.user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
                messages.success(request, f'Profile update for {change.user.name} approved.')

            elif action == 'reject':
                reason = request.POST.get('rejection_reason', '')
                change.status = 'rejected'
                change.rejection_reason = reason
                change.save()
                _log_action(request.user, 'edit', 'profile', str(change.pk), change.user.name, request, details=f'Rejected: {reason}')
                try:
                    send_mail(
                        '[BZSF] Profile update not approved',
                        f'Hi {change.user.name},\n\nYour profile update was not approved.\n'
                        f'Reason: {reason or "No reason provided"}\n\nDIU BZSF Team',
                        settings.DEFAULT_FROM_EMAIL,
                        [change.user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
                messages.info(request, f'Profile update for {change.user.name} rejected.')

        return redirect('accounts:verify_members')

    return render(request, 'accounts/verify_members.html', {
        'pending_accounts': pending_accounts,
        'pending_profiles': pending_profiles,
    })


