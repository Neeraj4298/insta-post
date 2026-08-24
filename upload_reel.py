import os
import sys
import subprocess
from pathlib import Path
from instagrapi import Client

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
THUMBNAIL_PATH = str(ROOT_DIR / "downloads" / "thumbnail.jpg")
FFMPEG_PATH = str(ROOT_DIR / "venv" / "bin" / "ffmpeg")
SESSION_FILE = str(ROOT_DIR / "downloads" / "session.json")

def generate_thumbnail(video_path: str, thumbnail_path: str) -> str:
    """Generates thumbnail frame from video using FFmpeg."""
    cmd = [
        FFMPEG_PATH if os.path.exists(FFMPEG_PATH) else "ffmpeg",
        "-y",
        "-ss", "00:00:01",
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        thumbnail_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return thumbnail_path

def challenge_code_handler(username, choice):
    """Callback when Instagram requests a security 6-digit code."""
    print(f"\n⚠️ Instagram Security Verification Code requested for @{username} (Choice: {choice})")
    print("Please check your registered Email / Phone for the 6-digit verification code.")
    code = input("Enter 6-digit verification code: ").strip()
    return code

def upload_instagram_reel():
    print(f"Initializing Instagram Client for @{USERNAME}...")
    cl = Client()
    cl.challenge_code_handler = challenge_code_handler

    # Reuse session if available
    if os.path.exists(SESSION_FILE):
        try:
            print("Loading existing session settings...")
            cl.load_settings(SESSION_FILE)
            cl.login(USERNAME, PASSWORD)
            print("✓ Logged in via saved session!")
        except Exception as e:
            print(f"Session load failed: {e}. Re-logging in...")
            cl.login(USERNAME, PASSWORD)
    else:
        print("Logging in with username & password...")
        cl.login(USERNAME, PASSWORD)

    # Save session for future requests
    cl.dump_settings(SESSION_FILE)
    print("✓ Logged in successfully!")

    if not os.path.exists(VIDEO_PATH):
        raise FileNotFoundError(f"Video file not found at {VIDEO_PATH}")

    print("Generating thumbnail image...")
    generate_thumbnail(VIDEO_PATH, THUMBNAIL_PATH)
    print(f"✓ Thumbnail generated at {THUMBNAIL_PATH}")

    print(f"Uploading Reel '{VIDEO_PATH}' to @{USERNAME}...")
    caption = "Dreamy Ghibli Moods ✨ #ghibli #anime #aesthetic #reels #tune_of_ghibli"

    media = cl.clip_upload(
        VIDEO_PATH,
        caption=caption,
        thumbnail=THUMBNAIL_PATH
    )

    print("\n==================================================")
    print(" 🎉 REEL UPLOADED SUCCESSFULLY TO INSTAGRAM!")
    print(f" Media ID: {media.pk}")
    print(f" Code: {media.code}")
    print(f" URL: https://www.instagram.com/reel/{media.code}/")
    print("==================================================")
    return media

if __name__ == "__main__":
    upload_instagram_reel()
