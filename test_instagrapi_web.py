import sys
from pathlib import Path
from instagrapi import Client

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
VIDEO_PATH = str(Path(__file__).resolve().parent / "downloads" / "reel_to_upload.mp4")
THUMBNAIL_PATH = str(Path(__file__).resolve().parent / "downloads" / "thumbnail.jpg")

def main():
    cl = Client()
    # Use standard Android device setting
    cl.set_device({
        "app_version": "269.0.0.18.75",
        "android_version": 26,
        "android_release": "8.0.0",
        "dpi": "480dpi",
        "resolution": "1080x1920",
        "manufacturer": "Samsung",
        "device": "greatqlte",
        "model": "SM-N950U",
        "cpu": "qcom",
        "version_code": "314665256"
    })
    print(f"Logging in to @{USERNAME}...")
    try:
        cl.login(USERNAME, PASSWORD)
        print("✓ Logged in successfully!")
        
        print("Uploading reel...")
        media = cl.clip_upload(VIDEO_PATH, caption="Dreamy Ghibli Moods ✨ #ghibli #anime #aesthetic", thumbnail=THUMBNAIL_PATH)
        print(f"✓ Reel uploaded successfully! Media URL: https://www.instagram.com/reel/{media.code}/")
    except Exception as e:
        print(f"❌ Upload error: {e}")

if __name__ == "__main__":
    main()
