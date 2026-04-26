from django.db import models
import uuid

GALLERY_CATEGORIES = [
    ('events',      'Events'),
    ('meetings',    'Meetings'),
    ('orientation', 'Orientation'),
    ('general',     'General'),
]

class GalleryPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=30, choices=GALLERY_CATEGORIES, default='general')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.caption or str(self.id)