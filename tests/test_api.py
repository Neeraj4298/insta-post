import os
import subprocess
import time
from fastapi.testclient import TestClient
from backend.main import app
from backend.utils.ffmpeg import get_ffmpeg_path

client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ClipForge Local API"
    assert data["status"] == "online"

def test_api_project_pipeline(tmp_path):
    ffmpeg_exe = get_ffmpeg_path()
    sample_video = str(tmp_path / "api_sample.mp4")

    cmd = [
        ffmpeg_exe, "-y",
        "-f", "lavfi", "-i", "testsrc=duration=2:size=320x240:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
        sample_video
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Post project
    post_res = client.post("/api/projects", json={"url_or_path": sample_video, "title": "API Test Project"})
    assert post_res.status_code == 200
    project = post_res.json()
    project_id = project["project_id"]
    assert project["title"] == "API Test Project"

    # Wait for background task to complete processing
    max_wait = 10
    start = time.time()
    completed = False
    while time.time() - start < max_wait:
        get_res = client.get(f"/api/projects/{project_id}")
        assert get_res.status_code == 200
        pdata = get_res.json()
        if pdata["status"] == "AUDIO_EXTRACTED":
            completed = True
            assert pdata["video_path"] is not None
            assert pdata["audio_path"] is not None
            break
        elif pdata["status"] == "FAILED":
            pytest.fail(f"Project processing failed: {pdata.get('error_message')}")
        time.sleep(0.5)

    assert completed, "Background task did not complete in time"

    # List projects
    list_res = client.get("/api/projects")
    assert list_res.status_code == 200
    all_projects = list_res.json()
    assert any(p["project_id"] == project_id for p in all_projects)
