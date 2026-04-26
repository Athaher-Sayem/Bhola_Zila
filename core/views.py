from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from notices.models import Notice
from accounts.models import User
from events.models import Event
from .models import HeroImage


def home(request):
    latest_notice = Notice.objects.first()
    members = User.objects.filter(is_verified=True, is_email_verified=True).select_related('profile')[:12]
    events = Event.objects.prefetch_related('images').all()[:3]
    hero_images = HeroImage.objects.all()[:8]
    return render(request, 'core/home.html', {
        'latest_notice': latest_notice,
        'members': members,
        'events': events,
        'hero_images': hero_images,
    })


def about(request):
    return render(request, 'core/about.html')


@login_required
def hero_upload(request):
    if not request.user.is_admin:
        messages.error(request, 'Admin only.')
        return redirect('core:home')
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        for img in images[:10]:
            HeroImage.objects.create(image=img)
        messages.success(request, f'{len(images)} hero image(s) uploaded.')
    return redirect('core:home')


@login_required
def hero_delete(request, pk):
    if request.user.is_admin and request.method == 'POST':
        get_object_or_404(HeroImage, pk=pk).delete()
        messages.success(request, 'Hero image deleted.')
    return redirect('core:home')