import os
import json
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.clip import ClipScores
from backend.engines.chunker import create_semantic_chunks
from backend.engines.scoring_engine import calculate_final_score
from backend.engines.candidate_detector import detect_candidates_in_chunks
from backend.services.analysis_service import analyze_project_transcript
from backend.utils.files import save_project_metadata, create_project_id, get_project_dir

client = TestClient(app)

@pytest.fixture
def mock_transcribed_project():
    pid = create_project_id()
    project_dir = get_project_dir(pid)
    transcript_path = project_dir / "transcript" / "transcript.json"

    sample_transcript = {
        "project_id": pid,
        "language": "en",
        "duration_seconds": 120.0,
        "segments": [
            {"id": 1, "start": 0.0, "end": 5.0, "text": "Welcome to today's talk about life and faith."},
            {"id": 2, "start": 5.1, "end": 25.0, "text": "Remember this truth: you were never meant to carry this heavy burden alone because hope changes everything."},
            {"id": 3, "start": 25.5, "end": 50.0, "text": "When you stop trying to fix yourself and start believing in grace, your whole perspective transforms."},
            {"id": 4, "start": 50.5, "end": 80.0, "text": "This is the most important lesson you will ever hear in your entire lifetime."},
            {"id": 5, "start": 80.5, "end": 115.0, "text": "Thank you for listening today."}
        ]
    }

    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(sample_transcript, f, indent=2)

    meta = {
        "project_id": pid,
        "title": "Intelligence Test Video",
        "source_url": "test",
        "status": "TRANSCRIBED",
        "transcript_path": str(transcript_path),
        "created_at": "2026-08-24T00:00:00Z"
    }
    save_project_metadata(pid, meta)
    return pid

def test_semantic_chunker():
    segments = [
        {"id": 1, "start": 0.0, "end": 10.0, "text": "Hello world."},
        {"id": 2, "start": 10.5, "end": 20.0, "text": "This is a test."}
    ]
    chunks = create_semantic_chunks(segments, target_duration=5.0)
    assert len(chunks) > 0
    assert chunks[0]["start"] == 0.0
    assert "Hello world." in chunks[0]["text"]

def test_scoring_formula():
    scores = ClipScores(
        hook=10.0,               # 10 * 0.25 = 2.5
        standalone_context=10.0, # 10 * 0.25 = 2.5
        message_completeness=10.0,# 10 * 0.20 = 2.0
        emotional_impact=10.0,   # 10 * 0.15 = 1.5
        curiosity=10.0,          # 10 * 0.10 = 1.0
        shareability=10.0        # 10 * 0.05 = 0.5
    )
    # Sum = 10.0 * 10 = 100.0
    final_score = calculate_final_score(scores)
    assert final_score == 100.0

def test_analysis_service(mock_transcribed_project):
    candidates = analyze_project_transcript(mock_transcribed_project)
    assert len(candidates) > 0
    first_cand = candidates[0]
    assert "candidate_id" in first_cand
    assert first_cand["final_score"] >= 50.0
    assert first_cand["duration"] >= 15.0 and first_cand["duration"] <= 90.0

def test_analysis_api_routes(mock_transcribed_project):
    analyze_res = client.post(f"/api/projects/{mock_transcribed_project}/analyze")
    assert analyze_res.status_code == 200

    # Synchronous run for deterministic test check
    analyze_project_transcript(mock_transcribed_project)

    cand_res = client.get(f"/api/projects/{mock_transcribed_project}/candidates")
    assert cand_res.status_code == 200
    cands = cand_res.json()
    assert len(cands) > 0
    assert cands[0]["project_id"] == mock_transcribed_project
