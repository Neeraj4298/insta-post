import os
import subprocess
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.video_service import ingest_video
from backend.services.audio_service import extract_project_audio
from backend.services.transcription_service import transcribe_project_audio
from backend.utils.ffmpeg import get_ffmpeg_path
from backend.utils.files import load_project_metadata

client = TestClient(app)

@pytest.fixture
def sample_project(tmp_path):
    ffmpeg_exe = get_ffmpeg_path()
    sample_video = str(tmp_path / "transcribe_sample.mp4")

    # Generate video with sine audio
    cmd = [
        ffmpeg_exe, "-y",
        "-f", "lavfi", "-i", "testsrc=duration=3:size=320x240:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
        sample_video
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    meta = ingest_video(sample_video, title="Transcription Test Video")
    meta_audio = extract_project_audio(meta["project_id"])
    return meta_audio["project_id"]

def test_transcription_service(sample_project):
    # Run transcription using faster-whisper (tiny model for fast testing)
    transcript_data = transcribe_project_audio(sample_project, model_name="tiny", compute_type="int8")

    assert transcript_data["project_id"] == sample_project
    assert "language" in transcript_data
    assert "segments" in transcript_data
    assert isinstance(transcript_data["segments"], list)

    meta = load_project_metadata(sample_project)
    assert meta["status"] == "TRANSCRIBED"
    assert meta["transcript_path"] is not None
    assert os.path.exists(meta["transcript_path"])

def test_transcription_api_routes(sample_project):
    # Test API trigger
    transcribe_res = client.post(f"/api/projects/{sample_project}/transcribe?model_name=tiny")
    assert transcribe_res.status_code == 200

    # Execute synchronous transcription for deterministic assertion
    transcribe_project_audio(sample_project, model_name="tiny")

    # Retrieve transcript
    get_res = client.get(f"/api/projects/{sample_project}/transcript")
    assert get_res.status_code == 200
    t_data = get_res.json()
    assert t_data["project_id"] == sample_project
    assert "segments" in t_data
