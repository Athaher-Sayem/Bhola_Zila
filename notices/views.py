from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notice
from .forms import NoticeForm
from bhola.email_utils import notify_all_users


def _log(user, action, target_type, target_id, target_name, request, details=""):
    try:
        from adminpanel.models import ActivityLog
        ActivityLog.objects.create(
            user=user, action=action,
            target_type=target_type, target_id=str(target_id),
            target_name=target_name, details=details,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
    except Exception:
        pass  # Never crash the real request

# def notice_list(request):
#     notices = Notice.objects.select_related('created_by').all()
#     return render(request, 'notices/list.html', {'notices': notices})

def notice_list(request):
    query = request.GET.get('q', '')
    notices = Notice.objects.select_related('created_by').all()
    if query:
        notices = notices.filter(title__icontains=query) | notices.filter(description__icontains=query)
    return render(request, 'notices/list.html', {'notices': notices, 'query': query})



@login_required
def notice_create(request):
    if not request.user.can_post:
        messages.error(request, 'Permission denied.')
        return redirect('notices:list')
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.created_by = request.user
            notice.save()
            _log(request.user, 'create', 'notice', notice.pk, notice.title, request)
            notify_all_users(
                    subject=f'[BZSF Notice] {notice.title}',
                    message=f'A new notice has been posted on BZSF.\n\nTitle: {notice.title}\n\n{notice.description[:500]}\n\n— BZSF Team',
                    audience=notice.email_audience,
                )
            messages.success(request, 'Notice posted!')
            return redirect('notices:list')
    else:
        form = NoticeForm()
    return render(request, 'notices/form.html', {'form': form})

@login_required
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.user.can_post:
        _log(request.user, 'delete', 'notice', notice.pk, notice.title, request)
        notice.delete()
    return redirect('notices:list')
