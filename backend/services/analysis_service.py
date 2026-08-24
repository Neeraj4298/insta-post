import json
import os
from pathlib import Path
from typing import Dict, Any, List

from backend.utils.files import get_project_dir, load_project_metadata, save_project_metadata
from backend.engines.chunker import create_semantic_chunks
from backend.engines.candidate_detector import detect_candidates_in_chunks
from backend.models.clip import ClipCandidate

def analyze_project_transcript(project_id: str, model_name: str = "llama3") -> List[Dict[str, Any]]:
    """
    Orchestrates Phase 3 Intelligence Pipeline:
    1. Loads transcript.json
    2. Chunks transcript into semantic segments
    3. Detects candidate reel moments (LLM / Heuristic)
    4. Computes deterministic potential scores out of 100
    5. Saves data/projects/{project_id}/analysis/candidates.json
    6. Updates metadata status to ANALYZED
    """
    meta = load_project_metadata(project_id)
    transcript_path = meta.get("transcript_path")

    if not transcript_path or not os.path.exists(transcript_path):
        meta["status"] = "FAILED"
        meta["error_message"] = "Transcript file not found. Run Phase 2 transcription first."
        save_project_metadata(project_id, meta)
        raise FileNotFoundError(f"Transcript for project {project_id} not found at {transcript_path}")

    meta["status"] = "ANALYZING"
    save_project_metadata(project_id, meta)

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_data = json.load(f)

        segments = transcript_data.get("segments", [])
        if not segments:
            raise ValueError("Transcript segments list is empty.")

        # 1. Semantic Chunker
        chunks = create_semantic_chunks(segments)

        # 2. Candidate Detector & Scoring Engine
        candidates: List[ClipCandidate] = detect_candidates_in_chunks(
            chunks=chunks,
            project_id=project_id,
            model_name=model_name
        )

        # Convert candidates to dict list
        cand_dict_list = [cand.model_dump() for cand in candidates]

        project_dir = get_project_dir(project_id)
        analysis_path = project_dir / "analysis" / "candidates.json"

        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(cand_dict_list, f, indent=2)

        meta["status"] = "ANALYZED"
        meta["candidates_path"] = str(analysis_path)
        meta["candidate_count"] = len(cand_dict_list)
        save_project_metadata(project_id, meta)

        return cand_dict_list

    except Exception as e:
        meta["status"] = "FAILED"
        meta["error_message"] = str(e)
        save_project_metadata(project_id, meta)
        raise e
