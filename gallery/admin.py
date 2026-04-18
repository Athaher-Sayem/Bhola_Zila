from django.contrib import admin
from .models import GalleryPhoto
@admin.register(GalleryPhoto)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['caption', 'uploaded_at']
