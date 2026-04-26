from django.db import models
import uuid, io, os
from django.core.files.base import ContentFile


def _compress_hero(upload_file):
    try:
        from PIL import Image as PILImage
        upload_file.seek(0)
        img = PILImage.open(upload_file)
        img.load()
        if img.mode not in ('RGB',):
            img = img.convert('RGB')
        img.thumbnail((1400, 900), PILImage.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        buf.seek(0)
        stem = os.path.splitext(os.path.basename(upload_file.name))[0]
        return ContentFile(buf.read(), name=f'{stem}.jpg')
    except Exception:
        upload_file.seek(0)
        return upload_file


class HeroImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='hero/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', '-uploaded_at']

    def save(self, *args, **kwargs):
        # Compress on first save only (when the image file is new)
        if self.pk is None and self.image:
            self.image = _compress_hero(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'HeroImage {self.order}'