from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from functools import wraps
from accounts.models import PendingProfileChange
from events.models import Event
from notices.models import Notice
from gallery.models import GalleryPhoto
from .models import ActivityLog
from accounts.models import User, Profile, PendingProfileChange


# ── decorator ──────────────────────────────────────────────────────────────
def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_admin:
            messages.error(request, 'Admin access required.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


# ── helpers ─────────────────────────────────────────────────────────────────
def _log(user, action, target_type, target_id, target_name, request, details=''):
    try:
        ActivityLog.objects.create(
            user=user,
            action=action,
            target_type=target_type,
            target_id=str(target_id),
            target_name=target_name,
            details=details,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
    except Exception:
        pass


# ── views ────────────────────────────────────────────────────────────────────
@admin_required
def dashboard(request):
    stats = {
        'total_users': User.objects.count(),
        'verified_users': User.objects.filter(is_verified=True).count(),
        'pending_accounts': User.objects.filter(
            is_email_verified=True, account_approved=False, account_rejected=False
        ).count(),
        'pending_profiles': PendingProfileChange.objects.filter(status='pending').count(),
        'unverified_email': User.objects.filter(is_email_verified=False).count(),
        'total_events': Event.objects.count(),
        'total_notices': Notice.objects.count(),
        'total_gallery': GalleryPhoto.objects.count(),
        'total_admins': User.objects.filter(role__in=['admin', 'second_admin']).count(),
    }
    recent_logs = ActivityLog.objects.select_related('user')[:15]
    recent_users = User.objects.order_by('-date_joined')[:8]
    return render(request, 'adminpanel/dashboard.html', {
        'stats': stats,
        'recent_logs': recent_logs,
        'recent_users': recent_users,
    })


@admin_required
def user_list(request):
    search = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    users = User.objects.select_related('profile').order_by('-date_joined')
    if search:
        users = users.filter(name__icontains=search) | users.filter(email__icontains=search) | users.filter(student_id__icontains=search)
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'adminpanel/users.html', {
        'users': users,
        'role_choices': User.ROLE_CHOICES,
    })


@admin_required
def user_action(request, pk):
    """POST-only: change role, toggle active, delete user."""
    if request.method != 'POST':
        return redirect('adminpanel:users')
    user = get_object_or_404(User, pk=pk)
    action = request.POST.get('action')

    if action == 'approve_account':
        user.account_approved = True
        user.is_verified = True
        user.account_rejected = False
        user.rejection_reason = ''
        user.save()
        _log(request.user, 'verify', 'user', user.pk, user.name, request, details='Account approved')
        messages.success(request, f'{user.name}\'s account approved.')

    elif action == 'reject_account':
        reason = request.POST.get('rejection_reason', '')
        user.account_rejected = True
        user.account_approved = False
        user.rejection_reason = reason
        user.save()
        _log(request.user, 'edit', 'user', user.pk, user.name, request, details=f'Account rejected: {reason}')
        messages.info(request, f'{user.name}\'s account rejected.')

    elif action == 'change_role':
        new_role = request.POST.get('role')
        if new_role in dict(User.ROLE_CHOICES):
            old_role = user.role
            user.role = new_role
            if new_role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            elif new_role != 'admin':
                user.is_staff = False
                user.is_superuser = False
            user.save()
            _log(request.user, 'edit', 'user', user.pk, user.name, request,
                 details=f'Role changed from {old_role} → {new_role}')
            messages.success(request, f'{user.name}\'s role changed to {new_role}.')

    elif action == 'toggle_active':
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        _log(request.user, 'edit', 'user', user.pk, user.name, request, details=f'Account {status}')
        messages.success(request, f'{user.name} has been {status}.')

    elif action == 'delete':
        name = user.name
        user.delete()
        _log(request.user, 'delete', 'user', pk, name, request)
        messages.success(request, f'{name} deleted.')

    elif action == 'verify':
        user.is_verified = True
        try:
            user.profile.pending_verification = False
            user.profile.save()
        except Profile.DoesNotExist:
            pass
        user.save()
        _log(request.user, 'verify', 'user', user.pk, user.name, request)
        messages.success(request, f'{user.name} verified.')

    return redirect('adminpanel:users')


@admin_required
def content_view(request):
    events = Event.objects.select_related('created_by').prefetch_related('images').all()
    notices = Notice.objects.select_related('created_by').all()
    photos = GalleryPhoto.objects.all()
    return render(request, 'adminpanel/content.html', {
        'events': events,
        'notices': notices,
        'photos': photos,
    })


@admin_required
def delete_event(request, pk):
    if request.method == 'POST':
        event = get_object_or_404(Event, pk=pk)
        _log(request.user, 'delete', 'event', event.pk, event.title, request)
        event.delete()
        messages.success(request, 'Event deleted.')
    return redirect('adminpanel:content')


@admin_required
def delete_notice(request, pk):
    if request.method == 'POST':
        notice = get_object_or_404(Notice, pk=pk)
        _log(request.user, 'delete', 'notice', notice.pk, notice.title, request)
        notice.delete()
        messages.success(request, 'Notice deleted.')
    return redirect('adminpanel:content')


@admin_required
def logs_view(request):
    action_filter = request.GET.get('action', '')
    target_filter = request.GET.get('target', '')
    logs = ActivityLog.objects.select_related('user')
    if action_filter:
        logs = logs.filter(action=action_filter)
    if target_filter:
        logs = logs.filter(target_type=target_filter)
    return render(request, 'adminpanel/logs.html', {
        'logs': logs[:300],
        'action_choices': ActivityLog.ACTION_CHOICES,
        'target_types': ActivityLog.objects.values_list('target_type', flat=True).distinct(),
    })



@admin_required
def profile_changes_view(request):
    """Admin page: review all profile change submissions."""
    from accounts.models import PendingProfileChange
    status_filter = request.GET.get('status', 'pending')
    changes = PendingProfileChange.objects.select_related(
        'user', 'user__profile', 'reviewed_by'
    )
    if status_filter:
        changes = changes.filter(status=status_filter)
    changes = changes[:200]

    if request.method == 'POST':
        from django.utils import timezone
        change_id = request.POST.get('change_id')
        action = request.POST.get('action')
        change = get_object_or_404(PendingProfileChange, pk=change_id)

        change.reviewed_by = request.user
        change.reviewed_at = timezone.now()

        if action == 'approve':
            change.status = 'approved'
            change.save()
            change.apply_to_profile()
            _log(request.user, 'verify', 'profile', change.pk, change.user.name, request)
            messages.success(request, f'Profile update for {change.user.name} approved and applied.')

        elif action == 'reject':
            reason = request.POST.get('rejection_reason', '')
            change.status = 'rejected'
            change.rejection_reason = reason
            change.save()
            _log(request.user, 'edit', 'profile', change.pk, change.user.name, request,
                 details=f'Profile rejected: {reason}')
            messages.info(request, f'Profile update for {change.user.name} rejected.')

        return redirect('adminpanel:profile_changes')

    return render(request, 'adminpanel/profile_changes.html', {
        'changes': changes,
        'status_filter': status_filter,
    })