import re
import os
from pathlib import Path
import gdown

def download_from_drive(drive_url: str, output_path: str) -> bool:
    """
    Extracts file ID from Google Drive URL and downloads the video file locally.
    """
    print(f"Downloading reel from Drive URL: {drive_url}...")
    try:
        # Match /d/<file_id>/ or id=<file_id>
        file_id_match = re.search(r'(?:/d/|id=)([a-zA-Z0-9_-]+)', drive_url)
        if file_id_match:
            file_id = file_id_match.group(1)
            direct_url = f'https://drive.google.com/uc?id={file_id}'
            gdown.download(direct_url, output_path, quiet=False)
        else:
            # Fallback direct gdown download
            gdown.download(drive_url, output_path, quiet=False, fuzzy=True)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✓ Downloaded successfully ({os.path.getsize(output_path)} bytes) to {output_path}")
            return True
        else:
            print("❌ Download failed: File is empty or does not exist.")
            return False
    except Exception as e:
        print(f"❌ Error downloading from Drive: {e}")
        return False

if __name__ == "__main__":
    # Test download
    test_url = "https://drive.google.com/drive/folders/1saR2zoFd47npssYG0PnUeY8HMD5Zky5o"
    print("Drive Downloader module initialized.")
