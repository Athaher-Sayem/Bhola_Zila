from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notice
from .forms import NoticeForm

def notice_list(request):
    notices = Notice.objects.select_related('created_by').all()
    return render(request, 'notices/list.html', {'notices': notices})

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
            messages.success(request, 'Notice posted!')
            return redirect('notices:list')
    else:
        form = NoticeForm()
    return render(request, 'notices/form.html', {'form': form})

@login_required
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.user.can_post:
        notice.delete()
    return redirect('notices:list')
