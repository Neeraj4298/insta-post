import os
import subprocess
import pytest
from backend.services.video_service import validate_input_source, ingest_video
from backend.services.audio_service import extract_project_audio
from backend.utils.ffmpeg import get_ffmpeg_path

def test_validate_input_source(tmp_path):
    # Non-existent file
    assert not validate_input_source("/tmp/non_existent_file_12345.mp4")
    # Valid URL syntax
    assert validate_input_source("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    # Valid existing file
    dummy_file = tmp_path / "dummy.mp4"
    dummy_file.write_text("test")
    assert validate_input_source(str(dummy_file))

def test_full_phase_1_service_pipeline(tmp_path):
    ffmpeg_exe = get_ffmpeg_path()
    sample_video = str(tmp_path / "sample.mp4")

    # Create dummy video
    cmd = [
        ffmpeg_exe, "-y",
        "-f", "lavfi", "-i", "testsrc=duration=3:size=320x240:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
        sample_video
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # 1. Ingest video
    meta = ingest_video(sample_video, title="Integration Test Video")
    assert meta["status"] == "DOWNLOADED"
    assert os.path.exists(meta["video_path"])
    assert meta["duration_seconds"] is not None

    # 2. Extract audio
    meta_audio = extract_project_audio(meta["project_id"])
    assert meta_audio["status"] == "AUDIO_EXTRACTED"
    assert meta_audio["audio_path"] is not None
    assert os.path.exists(meta_audio["audio_path"])
