# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from notices.models import Notice
from accounts.models import User
from events.models import Event
from .models import HeroImage
import io
import os
from PIL import Image as PILImage
from django.conf import settings


def compress_image(upload_file):
    try:
        upload_file.seek(0)
        img = PILImage.open(upload_file)
        img.load()
        if img.mode not in ('RGB',):
            img = img.convert('RGB')
        img.thumbnail((1200, 900), PILImage.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=78, optimize=True)
        buf.seek(0)
        stem = os.path.splitext(os.path.basename(upload_file.name))[0]
        return ContentFile(buf.read(), name=f'{stem}.jpg')
    except Exception:
        upload_file.seek(0)
        return upload_file  # fallback: save original


def home(request):
    latest_notice = Notice.objects.first()
    debug_custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'NOT SET')
    members = User.objects.filter(is_verified=True, is_email_verified=True).select_related('profile')[:12]
    events = Event.objects.prefetch_related('images').all()[:3]
    hero_images = HeroImage.objects.all()[:8]
    return render(request, 'core/home.html', {
        'latest_notice': latest_notice,
        'members': members,
        'events': events,
        'hero_images': hero_images,
        'debug_custom_domain': debug_custom_domain,
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
        for raw_img in images[:10]:
            compressed = compress_image(raw_img)   # <-- compression applied here
            HeroImage.objects.create(image=compressed)
        messages.success(request, f'{len(images)}  Image(s) uploaded.')
    return redirect('core:home')


@login_required
def hero_delete(request, pk):
    if request.user.is_admin and request.method == 'POST':
        get_object_or_404(HeroImage, pk=pk).delete()
        messages.success(request, 'Hero image deleted.')
    return redirect('core:home')