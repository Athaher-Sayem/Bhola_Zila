from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from .models import GalleryPhoto, GALLERY_CATEGORIES
import io, os

GALLERY_LIMIT = 200


def _compress(upload_file, max_side=1200):
    try:
        from PIL import Image as PILImage
        upload_file.seek(0)
        img = PILImage.open(upload_file)
        img.load()
        if img.mode not in ('RGB',):
            img = img.convert('RGB')
        img.thumbnail((max_side, max_side), PILImage.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=78, optimize=True)
        buf.seek(0)
        stem = os.path.splitext(os.path.basename(upload_file.name))[0]
        return ContentFile(buf.read(), name=f'{stem}.jpg')
    except Exception:
        upload_file.seek(0)
        return upload_file


def gallery_view(request):
    category = request.GET.get('category', '')
    photos = GalleryPhoto.objects.all()[:GALLERY_LIMIT]
    if category:
        photos = GalleryPhoto.objects.filter(category=category)[:GALLERY_LIMIT]
    return render(request, 'gallery/gallery.html', {
        'photos': photos,
        'categories': GALLERY_CATEGORIES,
        'active_category': category,
    })


@login_required
def gallery_upload(request):
    if not request.user.is_admin:
        messages.error(request, 'Only admin can manage gallery.')
        return redirect('gallery:gallery')
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        category = request.POST.get('category', 'general')
        caption = request.POST.get('caption', '')
        current_count = GalleryPhoto.objects.count()
        slots = max(0, GALLERY_LIMIT - current_count)
        uploaded = 0
        for img in images[:slots]:
            compressed = _compress(img)
            GalleryPhoto.objects.create(image=compressed, caption=caption, category=category)
            uploaded += 1
        if uploaded:
            messages.success(request, f'{uploaded} photo(s) uploaded!')
        else:
            messages.warning(request, f'Gallery is full ({GALLERY_LIMIT} photos max).')
        return redirect('gallery:gallery')
    return render(request, 'gallery/upload.html', {'categories': GALLERY_CATEGORIES})


@login_required
def gallery_delete(request, pk):
    if request.user.is_admin:
        get_object_or_404(GalleryPhoto, pk=pk).delete()
    return redirect('gallery:gallery')