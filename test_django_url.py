import os

# Force DEBUG=True for local testing
os.environ['DEBUG'] = 'True'

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhola.settings')
django.setup()

from django.conf import settings

print("=" * 60)
print("DJANGO S3 URL GENERATION TEST")
print("=" * 60)
print(f"DEBUG: {settings.DEBUG}")
print(f"Storage backend: {settings.STORAGES['default']['BACKEND']}")

# Check if S3 settings exist
print(f"\n📋 S3 Settings:")
print(f"   AWS_S3_ENDPOINT_URL: {getattr(settings, 'AWS_S3_ENDPOINT_URL', 'NOT SET (using local filesystem)')}")
print(f"   AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'NOT SET')}")

# If S3 is not configured, show what storage is active
if hasattr(settings, 'AWS_S3_ENDPOINT_URL'):
    from django.core.files.storage import default_storage
    
    print(f"\n🧪 Testing URL generation:")
    test_paths = [
        "hero/Jersy.jpg",
        "hero/Vice.jpg",
        "gallery/oi-24.jpg",
    ]
    
    for path in test_paths:
        try:
            url = default_storage.url(path)
            print(f"\n   Path: {path}")
            print(f"   URL: {url}")
        except Exception as e:
            print(f"\n   Path: {path}")
            print(f"   Error: {e}")
    
    print(f"\n✅ Expected correct Supabase URL:")
    endpoint = settings.AWS_S3_ENDPOINT_URL
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    print(f"   {endpoint}/object/public/{bucket}/hero/Jersy.jpg")
else:
    print("\n⚠️  S3 is NOT configured (DEBUG=True uses local filesystem)")
    print("   Your production site uses S3 at:")
    print("   https://iubicmwwjmpnwsabzdvb.supabase.co/storage/v1/object/public/media/")

print("\n" + "=" * 60)
print("\n💡 Since your production site is on Vercel/Render,")
print("   this test only works locally with DEBUG=True")
print("   (which uses local filesystem, not S3)")
print("=" * 60)