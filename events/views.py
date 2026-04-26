from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from .models import Event, EventImage
from .forms import EventForm
import io, os
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




def compress_image(upload_file):
    """Compress any image to JPEG ≤ 1200×900 at quality 78."""
    try:
        from PIL import Image as PILImage
        upload_file.seek(0)
        img = PILImage.open(upload_file)
        img.load()  # force read before seek issues
        if img.mode not in ('RGB',):
            img = img.convert('RGB')
        img.thumbnail((1200, 900), PILImage.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=78, optimize=True)
        buf.seek(0)
        stem = os.path.splitext(os.path.basename(upload_file.name))[0]
        return ContentFile(buf.read(), name=f'{stem}.jpg')
    except Exception as e:
        upload_file.seek(0)
        return upload_file   # fallback: save original


def event_list(request):
    events = Event.objects.prefetch_related('images').all()
    return render(request, 'events/list.html', {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/detail.html', {'event': event})


@login_required
def event_create(request):
    if not request.user.can_post:
        messages.error(request, 'Permission denied.')
        return redirect('events:list')
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            _log(request.user, 'create', 'event', event.pk, event.title, request)
            notify_all_users(
                subject=f'[BZSF Event] {event.title}',
                message=f'A new event has been posted on BZSF.\n\nTitle: {event.title}\n\n{event.description[:500]}\n\n— BHOLA Team',
                audience='all',
            )
            for raw_img in form.cleaned_data['images']:   # ← use form data, not request.FILES
                compressed = compress_image(raw_img)
                EventImage.objects.create(event=event, image=compressed)
            messages.success(request, 'Event posted successfully!')
            return redirect('events:list')
    else:
        form = EventForm()
    return render(request, 'events/form.html', {'form': form})





@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user.is_admin or event.created_by == request.user:
        _log(request.user, 'delete', 'event', event.pk, event.title, request)
        event.delete()
        messages.success(request, 'Event deleted.')
    return redirect('events:list')
