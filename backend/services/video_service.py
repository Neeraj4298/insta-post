import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import yt_dlp as ytdl  # type: ignore

from backend.utils.files import get_project_dir, save_project_metadata, create_project_id
from backend.utils.ffmpeg import get_ffmpeg_path, get_media_info

def validate_input_source(url_or_path: str) -> bool:
    """Check if input is a valid URL or existing local video file."""
    if os.path.exists(url_or_path):
        return True
    if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
        return True
    return False

def ingest_video(url_or_path: str, project_id: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
    """
    Downloads or copies video into project source folder.
    Returns metadata dict with project details.
    """
    if not validate_input_source(url_or_path):
        raise ValueError(f"Invalid URL or local video path: {url_or_path}")

    if not project_id:
        project_id = create_project_id()

    project_dir = get_project_dir(project_id)
    source_dir = project_dir / "source"
    target_video_path = source_dir / "video.mp4"

    video_title = title or "Untitled Video"

    if os.path.exists(url_or_path):
        # Local video file provided
        shutil.copy(url_or_path, target_video_path)
        if not title:
            video_title = Path(url_or_path).stem
    else:
        # YouTube or web URL
        ffmpeg_exe = get_ffmpeg_path()
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': str(target_video_path),
            'ffmpeg_location': ffmpeg_exe,
            'quiet': True,
            'no_warnings': True,
        }
        with ytdl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_or_path, download=True)
            if info:
                video_title = title or info.get('title', video_title)

    media_info = get_media_info(str(target_video_path))

    from datetime import datetime, timezone
    meta = {
        "project_id": project_id,
        "title": video_title,
        "source_url": url_or_path,
        "status": "DOWNLOADED",
        "video_path": str(target_video_path),
        "audio_path": None,
        "duration_seconds": media_info.get("duration_seconds"),
        "error_message": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    save_project_metadata(project_id, meta)
    return meta
