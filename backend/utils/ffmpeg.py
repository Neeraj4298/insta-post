import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

def get_ffmpeg_path() -> str:
    # 1. Check venv/bin/ffmpeg
    venv_ffmpeg = Path(__file__).resolve().parent.parent.parent / "venv" / "bin" / "ffmpeg"
    if venv_ffmpeg.exists():
        return str(venv_ffmpeg)
    
    # 2. Check imageio_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    
    # 3. Check system PATH
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
        
    raise RuntimeError("FFmpeg executable not found. Please ensure FFmpeg is available.")

def extract_audio(video_path: str, output_audio_path: str, sample_rate: int = 16000) -> str:
    """Extract audio from video file to 16kHz mono WAV file (optimal for Whisper/transcription)."""
    ffmpeg_exe = get_ffmpeg_path()
    
    output_dir = os.path.dirname(output_audio_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    cmd = [
        ffmpeg_exe,
        "-y",                  # overwrite
        "-i", video_path,       # input
        "-vn",                 # disable video
        "-acodec", "pcm_s16le", # 16-bit PCM WAV
        "-ar", str(sample_rate),# 16000 Hz
        "-ac", "1",            # mono
        output_audio_path
    ]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed: {result.stderr}")
        
    return output_audio_path

def get_media_info(file_path: str) -> Dict[str, Any]:
    """Retrieve video duration using ffmpeg/ffprobe."""
    ffmpeg_exe = get_ffmpeg_path()
    cmd = [
        ffmpeg_exe,
        "-i", file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # FFmpeg outputs file info to stderr
    stderr = result.stderr
    duration = None
    import re
    dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr)
    if dur_match:
        hours, mins, secs = dur_match.groups()
        duration = float(hours) * 3600 + float(mins) * 60 + float(secs)
        
    return {
        "file_path": file_path,
        "duration_seconds": duration,
        "raw_info": stderr[:500]
    }
