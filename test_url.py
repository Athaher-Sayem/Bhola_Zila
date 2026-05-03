import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhola.settings')
django.setup()

# Import your models - adjust the import based on your app structure
from gallery.models import GalleryPhoto  # or whatever your image model is
# from core.models import YourModel  # if images are in another app

# Get the first image object
try:
    photo = GalleryPhoto.objects.first()
    if photo and photo.photo:  # assuming the field is called 'photo'
        print(f"✅ Found image object")
        print(f"📸 Image field URL: {photo.photo.url}")
        print(f"📁 Image field path: {photo.photo.name}")
    else:
        print("❌ No images found in database")
        
    # Also check all objects
    all_photos = GalleryPhoto.objects.all()
    print(f"\n📊 Total photos in database: {all_photos.count()}")
    for p in all_photos:
        print(f"   - {p.photo.name} → {p.photo.url}")
        
except ImportError:
    print("⚠️  Couldn't import Photo model. Try these instead:")
    print("   from gallery.models import Gallery")
    print("   from core.models import SomeModel")
except Exception as e:
    print(f"❌ Error: {e}")