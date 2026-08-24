import json
import os
from pathlib import Path
from typing import Dict, Any, List

from backend.utils.files import get_project_dir, load_project_metadata, save_project_metadata
from backend.engines.deduplicator import rank_and_filter_candidates

def rank_project_candidates(
    project_id: str,
    min_score: float = 65.0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Orchestrates Phase 4 Ranking Pipeline:
    1. Loads candidates.json from Phase 3 analysis
    2. Filters & deduplicates candidates
    3. Ranks Top N candidates
    4. Saves data/projects/{project_id}/analysis/ranked_clips.json
    5. Updates metadata status to READY_FOR_REVIEW
    """
    meta = load_project_metadata(project_id)
    candidates_path = meta.get("candidates_path")

    if not candidates_path or not os.path.exists(candidates_path):
        meta["status"] = "FAILED"
        meta["error_message"] = "Candidates file not found. Run Phase 3 analysis first."
        save_project_metadata(project_id, meta)
        raise FileNotFoundError(f"Candidates file for project {project_id} not found at {candidates_path}")

    meta["status"] = "RANKING"
    save_project_metadata(project_id, meta)

    try:
        with open(candidates_path, "r", encoding="utf-8") as f:
            candidates = json.load(f)

        ranked = rank_and_filter_candidates(
            candidates,
            min_score=min_score,
            limit=limit
        )

        project_dir = get_project_dir(project_id)
        ranked_path = project_dir / "analysis" / "ranked_clips.json"

        with open(ranked_path, "w", encoding="utf-8") as f:
            json.dump(ranked, f, indent=2)

        meta["status"] = "READY_FOR_REVIEW"
        meta["ranked_clips_path"] = str(ranked_path)
        meta["ranked_count"] = len(ranked)
        save_project_metadata(project_id, meta)

        return ranked

    except Exception as e:
        meta["status"] = "FAILED"
        meta["error_message"] = str(e)
        save_project_metadata(project_id, meta)
        raise e
