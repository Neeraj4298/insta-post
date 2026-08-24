import os
import json
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.engines.deduplicator import remove_overlapping_candidates, apply_diversity_spacing, rank_and_filter_candidates
from backend.services.clip_service import rank_project_candidates
from backend.utils.files import save_project_metadata, create_project_id, get_project_dir

client = TestClient(app)

@pytest.fixture
def mock_analyzed_project():
    pid = create_project_id()
    project_dir = get_project_dir(pid)
    candidates_path = project_dir / "analysis" / "candidates.json"

    raw_candidates = [
        # Overlapping clips A and B at ~10s-50s
        {
            "candidate_id": "cand_1", "project_id": pid, "start": 10.0, "end": 45.0, "duration": 35.0,
            "title": "Clip A - High Score", "hook": "Hook A", "reason": "Reason A",
            "scores": {"hook": 9.0, "standalone_context": 9.0, "message_completeness": 9.0, "emotional_impact": 9.0, "curiosity": 9.0, "shareability": 9.0},
            "final_score": 90.0
        },
        {
            "candidate_id": "cand_2", "project_id": pid, "start": 20.0, "end": 50.0, "duration": 30.0,
            "title": "Clip B - Lower Score Overlapping", "hook": "Hook B", "reason": "Reason B",
            "scores": {"hook": 7.0, "standalone_context": 7.0, "message_completeness": 7.0, "emotional_impact": 7.0, "curiosity": 7.0, "shareability": 7.0},
            "final_score": 70.0
        },
        # Spaced clip C at 120s-160s
        {
            "candidate_id": "cand_3", "project_id": pid, "start": 120.0, "end": 160.0, "duration": 40.0,
            "title": "Clip C - Separate Section", "hook": "Hook C", "reason": "Reason C",
            "scores": {"hook": 8.5, "standalone_context": 8.5, "message_completeness": 8.5, "emotional_impact": 8.5, "curiosity": 8.5, "shareability": 8.5},
            "final_score": 85.0
        }
    ]

    with open(candidates_path, "w", encoding="utf-8") as f:
        json.dump(raw_candidates, f, indent=2)

    meta = {
        "project_id": pid, "title": "Ranking Test Video", "source_url": "test",
        "status": "ANALYZED", "candidates_path": str(candidates_path), "created_at": "2026-08-24T00:00:00Z"
    }
    save_project_metadata(pid, meta)
    return pid

def test_overlap_deduplication():
    cands = [
        {"start": 10.0, "end": 40.0, "final_score": 90.0, "name": "A"},
        {"start": 20.0, "end": 50.0, "final_score": 70.0, "name": "B"}
    ]
    deduped = remove_overlapping_candidates(cands)
    assert len(deduped) == 1
    assert deduped[0]["name"] == "A"  # Higher score kept

def test_diversity_spacing():
    cands = [
        {"start": 10.0, "end": 40.0, "final_score": 90.0},
        {"start": 30.0, "end": 60.0, "final_score": 80.0}, # Close
        {"start": 120.0, "end": 150.0, "final_score": 85.0} # Spaced
    ]
    spaced = apply_diversity_spacing(cands, min_gap_seconds=60.0)
    assert len(spaced) == 2
    assert spaced[0]["start"] == 10.0
    assert spaced[1]["start"] == 120.0

def test_clip_ranking_service(mock_analyzed_project):
    ranked = rank_project_candidates(mock_analyzed_project)
    assert len(ranked) == 2
    assert ranked[0]["candidate_id"] == "cand_1"  # Highest score 90.0
    assert ranked[1]["candidate_id"] == "cand_3"  # Second highest 85.0 (cand_2 filtered out due to overlap)

def test_ranking_api_routes(mock_analyzed_project):
    res_post = client.post(f"/api/projects/{mock_analyzed_project}/rank")
    assert res_post.status_code == 200

    # Synchronous run for test checking
    rank_project_candidates(mock_analyzed_project)

    res_get = client.get(f"/api/projects/{mock_analyzed_project}/ranked")
    assert res_get.status_code == 200
    ranked_list = res_get.json()
    assert len(ranked_list) == 2
    assert ranked_list[0]["final_score"] >= ranked_list[1]["final_score"]
