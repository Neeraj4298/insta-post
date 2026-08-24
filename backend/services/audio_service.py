import os
from typing import Dict, Any
from backend.utils.files import get_project_dir, save_project_metadata, load_project_metadata
from backend.utils.ffmpeg import extract_audio

def extract_project_audio(project_id: str) -> Dict[str, Any]:
    """
    Extracts 16kHz WAV audio from the project source video.
    Updates project metadata with audio_path and AUDIO_EXTRACTED status.
    """
    meta = load_project_metadata(project_id)
    video_path = meta.get("video_path")

    if not video_path or not os.path.exists(video_path):
        meta["status"] = "FAILED"
        meta["error_message"] = "Source video file not found"
        save_project_metadata(project_id, meta)
        raise FileNotFoundError(f"Source video for project {project_id} not found at {video_path}")

    project_dir = get_project_dir(project_id)
    audio_path = project_dir / "audio" / "audio.wav"

    meta["status"] = "EXTRACTING_AUDIO"
    save_project_metadata(project_id, meta)

    extract_audio(str(video_path), str(audio_path), sample_rate=16000)

    meta["status"] = "AUDIO_EXTRACTED"
    meta["audio_path"] = str(audio_path)
    save_project_metadata(project_id, meta)

    return meta
