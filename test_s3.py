import os
import boto3
from botocore.config import Config

# -----------------------------------------------------------------
# 1. Define the values – use empty strings as placeholders
#    (they will be replaced by your real env vars)
# -----------------------------------------------------------------
ENDPOINT = "https://iubicmwwjmpnwsabzdvb.supabase.co/storage/v1/s3"   # optional placeholder
ACCESS_KEY = "30b481dc2ee3947d3d72a8c61e45d875"
SECRET_KEY = "45d99d5074df1c7f110d207baf4579a61032fd2256e6783d1eeaee20b0449e91"
BUCKET_NAME = "media"

# -----------------------------------------------------------------
# 2. Override with your environment variables (from Vercel / .env)
# -----------------------------------------------------------------
ENDPOINT    = os.environ.get("SUPABASE_S3_ENDPOINT", ENDPOINT)
ACCESS_KEY  = os.environ.get("SUPABASE_S3_ACCESS_KEY", ACCESS_KEY)
SECRET_KEY  = os.environ.get("SUPABASE_S3_SECRET_KEY", SECRET_KEY)
BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", BUCKET_NAME)

# -----------------------------------------------------------------
# 3. Test the connection
# -----------------------------------------------------------------
print(f"🔌 Endpoint : {ENDPOINT}")
print(f"📦 Bucket    : {BUCKET_NAME}")

try:
    s3 = boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name="us-east-1",           # dummy but required
        config=Config(signature_version="s3v4"),
    )
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    if "Contents" in response:
        print(f"✅ Success! {len(response['Contents'])} object(s):")
        for obj in response["Contents"]:
            print(f"   - {obj['Key']}  ({obj['Size']} bytes)")
    else:
        print("✅ Connection works. Bucket is empty.")

except Exception as e:
    print(f"❌ Failed: {e}")