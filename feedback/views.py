from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Feedback
from .forms import FeedbackForm, FeedbackResponseForm


def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.is_anonymous = not bool(fb.submitter_name)
            fb.save()
            return redirect('feedback:thanks')
    else:
        form = FeedbackForm()
    return render(request, 'feedback/submit.html', {'form': form})


def thanks(request):
    return render(request, 'feedback/thanks.html')


@login_required
def feedback_list(request):
    if not (request.user.is_admin or request.user.is_second_admin):
        messages.error(request, 'Admin access required.')
        return redirect('core:home')
    status_filter = request.GET.get('status', '')
    items = Feedback.objects.all()
    if status_filter:
        items = items.filter(status=status_filter)
    return render(request, 'feedback/list.html', {
        'items': items,
        'status_filter': status_filter,
    })


@login_required
def feedback_detail(request, pk):
    if not (request.user.is_admin or request.user.is_second_admin):
        messages.error(request, 'Admin access required.')
        return redirect('core:home')
    item = get_object_or_404(Feedback, pk=pk)
    if request.method == 'POST':
        form = FeedbackResponseForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Response saved.')
            return redirect('feedback:detail', pk=pk)
    else:
        form = FeedbackResponseForm(instance=item)
    return render(request, 'feedback/detail.html', {'item': item, 'form': form})