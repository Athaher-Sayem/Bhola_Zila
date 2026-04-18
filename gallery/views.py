from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import GalleryPhoto

def gallery_view(request):
    photos = GalleryPhoto.objects.all()[:20]
    return render(request, 'gallery/gallery.html', {'photos': photos})

@login_required
def gallery_upload(request):
    if not request.user.is_admin:
        messages.error(request, 'Only admin can manage gallery.')
        return redirect('gallery:gallery')
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        current_count = GalleryPhoto.objects.count()
        for img in images[:max(0, 20 - current_count)]:
            GalleryPhoto.objects.create(image=img, caption=request.POST.get('caption', ''))
        messages.success(request, 'Photos uploaded!')
        return redirect('gallery:gallery')
    return render(request, 'gallery/upload.html')

@login_required
def gallery_delete(request, pk):
    if request.user.is_admin:
        get_object_or_404(GalleryPhoto, pk=pk).delete()
    return redirect('gallery:gallery')
