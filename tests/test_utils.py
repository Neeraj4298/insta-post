import os
import tempfile
import pytest
from pathlib import Path

from backend.utils.files import get_project_dir, create_project_id, save_project_metadata, load_project_metadata
from backend.utils.ffmpeg import get_ffmpeg_path, extract_audio, get_media_info

def test_project_id_generation():
    pid = create_project_id()
    assert pid.startswith("proj_")
    assert len(pid) > 5

def test_metadata_save_and_load():
    pid = create_project_id()
    data = {"project_id": pid, "status": "TEST", "value": 123}
    save_project_metadata(pid, data)
    loaded = load_project_metadata(pid)
    assert loaded["project_id"] == pid
    assert loaded["status"] == "TEST"
    assert loaded["value"] == 123

def test_ffmpeg_path_and_media_info(tmp_path):
    ffmpeg_exe = get_ffmpeg_path()
    assert os.path.exists(ffmpeg_exe)

    # Generate a dummy 2-second video using ffmpeg
    video_path = str(tmp_path / "test_video.mp4")
    import subprocess
    cmd = [
        ffmpeg_exe, "-y",
        "-f", "lavfi", "-i", "testsrc=duration=2:size=320x240:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
        video_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert res.returncode == 0
    assert os.path.exists(video_path)

    # Test get_media_info
    info = get_media_info(video_path)
    assert info["duration_seconds"] is not None
    assert info["duration_seconds"] >= 1.9

    # Test extract_audio
    audio_path = str(tmp_path / "audio.wav")
    extracted = extract_audio(video_path, audio_path)
    assert os.path.exists(extracted)
    assert os.path.getsize(extracted) > 0
