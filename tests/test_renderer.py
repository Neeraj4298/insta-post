import os
import json
import subprocess
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.utils.subtitles import generate_srt_subtitles, format_timestamp_srt
from backend.utils.ffmpeg import get_ffmpeg_path, get_media_info
from backend.services.render_service import render_single_clip, render_project_clips
from backend.utils.files import save_project_metadata, create_project_id, get_project_dir

client = TestClient(app)

def test_srt_formatting():
    formatted = format_timestamp_srt(65.5)
    assert formatted == "00:01:05,500"

def test_srt_subtitle_generation(tmp_path):
    segments = [
        {"id": 1, "start": 10.0, "end": 15.0, "text": "First line of reel."},
        {"id": 2, "start": 15.5, "end": 20.0, "text": "Second line of reel."}
    ]
    srt_out = str(tmp_path / "test.srt")
    generate_srt_subtitles(segments, clip_start=10.0, clip_end=20.0, output_srt_path=srt_out)

    assert os.path.exists(srt_out)
    with open(srt_out, "r") as f:
        content = f.read()

    assert "FIRST LINE OF REEL." in content
    assert "00:00:00,000 --> 00:00:05,000" in content

@pytest.fixture
def mock_renderable_project(tmp_path):
    pid = create_project_id()
    project_dir = get_project_dir(pid)

    ffmpeg_exe = get_ffmpeg_path()
    sample_video = str(project_dir / "source" / "video.mp4")

    # Generate 5-second test MP4
    cmd = [
        ffmpeg_exe, "-y",
        "-f", "lavfi", "-i", "testsrc=duration=5:size=640x360:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=5",
        sample_video
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    ranked_path = project_dir / "analysis" / "ranked_clips.json"
    transcript_path = project_dir / "transcript" / "transcript.json"

    ranked_data = [
        {
            "candidate_id": "cand_reel_1", "project_id": pid, "start": 1.0, "end": 4.0, "duration": 3.0,
            "title": "Render Test Reel", "hook": "Test Hook", "reason": "Test Reason",
            "scores": {"hook": 8.0, "standalone_context": 8.0, "message_completeness": 8.0, "emotional_impact": 8.0, "curiosity": 8.0, "shareability": 8.0},
            "final_score": 80.0
        }
    ]

    transcript_data = {
        "project_id": pid, "language": "en", "duration_seconds": 5.0,
        "segments": [{"id": 1, "start": 1.0, "end": 4.0, "text": "Testing video render pipeline."}]
    }

    with open(ranked_path, "w") as f:
        json.dump(ranked_data, f)
    with open(transcript_path, "w") as f:
        json.dump(transcript_data, f)

    meta = {
        "project_id": pid, "title": "Render Test Project", "source_url": sample_video,
        "status": "READY_FOR_REVIEW", "video_path": sample_video,
        "ranked_clips_path": str(ranked_path), "transcript_path": str(transcript_path),
        "created_at": "2026-08-24T00:00:00Z"
    }
    save_project_metadata(pid, meta)
    return pid

def test_single_clip_rendering(mock_renderable_project):
    pdir = get_project_dir(mock_renderable_project)
    src_video = str(pdir / "source" / "video.mp4")
    out_mp4 = str(pdir / "output" / "test_single.mp4")

    rendered = render_single_clip(src_video, start=1.0, end=3.0, output_mp4_path=out_mp4, aspect_ratio="9:16")
    assert os.path.exists(rendered)

    info = get_media_info(rendered)
    assert info["duration_seconds"] is not None
    assert abs(info["duration_seconds"] - 2.0) <= 0.5

def test_full_render_service(mock_renderable_project):
    results = render_project_clips(mock_renderable_project, aspect_ratio="9:16")
    assert len(results) == 1
    assert os.path.exists(results[0]["output_path"])

def test_render_api_routes(mock_renderable_project):
    res_post = client.post(f"/api/projects/{mock_renderable_project}/render")
    assert res_post.status_code == 200

    # Synchronous run for test check
    render_project_clips(mock_renderable_project)

    # Check file serving
    res_file = client.get(f"/api/projects/{mock_renderable_project}/output/cand_reel_1.mp4")
    assert res_file.status_code == 200
    assert res_file.headers["content-type"] == "video/mp4"
