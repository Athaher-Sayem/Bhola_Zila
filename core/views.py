from django.shortcuts import render
from notices.models import Notice
from accounts.models import User
from events.models import Event

def home(request):
    latest_notice = Notice.objects.first()   # already ordered by -created_at
    members = User.objects.filter(is_verified=True, is_email_verified=True).select_related('profile')[:12]
    events = Event.objects.prefetch_related('images').all()[:3]
    return render(request, 'core/home.html', {
        'latest_notice': latest_notice,
        'members': members,
        'events': events,
    })

def about(request):
    return render(request, 'core/about.html')
