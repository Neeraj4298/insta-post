import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from pathlib import Path

from backend.models.project import ProjectCreate, ProjectResponse, ProjectStatus
from backend.services.video_service import ingest_video
from backend.services.audio_service import extract_project_audio
from backend.utils.files import DATA_DIR, load_project_metadata, save_project_metadata, create_project_id

router = APIRouter(prefix="/api/projects", tags=["projects"])

def run_phase_1_pipeline(project_id: str, url_or_path: str, title: str = None):
    try:
        # Step 1: Download / Ingest Video
        ingest_video(url_or_path, project_id=project_id, title=title)
        # Step 2: Extract Audio
        extract_project_audio(project_id)
    except Exception as e:
        try:
            meta = load_project_metadata(project_id)
            meta["status"] = ProjectStatus.FAILED
            meta["error_message"] = str(e)
            save_project_metadata(project_id, meta)
        except Exception:
            pass

@router.post("", response_model=ProjectResponse)
def create_project(payload: ProjectCreate, background_tasks: BackgroundTasks):
    """
    Create a new project from URL or local video path.
    Triggers Phase 1 Ingestion and Audio Extraction.
    """
    project_id = create_project_id()
    from datetime import datetime, timezone

    initial_meta = {
        "project_id": project_id,
        "title": payload.title or "Processing Video...",
        "source_url": payload.url_or_path,
        "status": ProjectStatus.DOWNLOADING,
        "video_path": None,
        "audio_path": None,
        "duration_seconds": None,
        "error_message": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    save_project_metadata(project_id, initial_meta)
    background_tasks.add_task(run_phase_1_pipeline, project_id, payload.url_or_path, payload.title)

    return ProjectResponse(**initial_meta)

@router.get("", response_model=List[ProjectResponse])
def list_projects():
    """List all projects in the workspace."""
    results = []
    if DATA_DIR.exists():
        for proj_dir in DATA_DIR.iterdir():
            if proj_dir.is_dir():
                meta_path = proj_dir / "metadata.json"
                if meta_path.exists():
                    try:
                        meta = load_project_metadata(proj_dir.name)
                        results.append(ProjectResponse(**meta))
                    except Exception:
                        pass
    return results

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str):
    """Get project status and details by ID."""
    try:
        meta = load_project_metadata(project_id)
        return ProjectResponse(**meta)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

@router.post("/{project_id}/transcribe")
def transcribe_project(project_id: str, background_tasks: BackgroundTasks, model_name: str = "base"):
    """Trigger Phase 2: Transcribe project audio using faster-whisper."""
    try:
        meta = load_project_metadata(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    if not meta.get("audio_path") or not os.path.exists(meta.get("audio_path")):
        raise HTTPException(status_code=400, detail="Audio file not extracted yet. Run Phase 1 first.")

    from backend.services.transcription_service import transcribe_project_audio
    background_tasks.add_task(transcribe_project_audio, project_id, model_name)
    return {"message": "Transcription task started", "project_id": project_id, "status": "TRANSCRIBING"}

@router.get("/{project_id}/transcript")
def get_project_transcript(project_id: str):
    """Retrieve saved transcript JSON for a project."""
    try:
        meta = load_project_metadata(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    transcript_path = meta.get("transcript_path")
    if not transcript_path or not os.path.exists(transcript_path):
        raise HTTPException(status_code=404, detail="Transcript not found for this project")

    import json
    with open(transcript_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@router.post("/{project_id}/analyze")
def analyze_project(project_id: str, background_tasks: BackgroundTasks, model_name: str = "llama3"):
    """Trigger Phase 3: Analyze transcript chunks and generate clip potential candidates."""
    try:
        meta = load_project_metadata(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    if not meta.get("transcript_path") or not os.path.exists(meta.get("transcript_path")):
        raise HTTPException(status_code=400, detail="Transcript not found. Run Phase 2 transcription first.")

    from backend.services.analysis_service import analyze_project_transcript
    background_tasks.add_task(analyze_project_transcript, project_id, model_name)
    return {"message": "Intelligence analysis task started", "project_id": project_id, "status": "ANALYZING"}

@router.get("/{project_id}/candidates")
def get_project_candidates(project_id: str):
    """Retrieve generated clip potential candidates for a project."""
    try:
        meta = load_project_metadata(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    candidates_path = meta.get("candidates_path")
    if not candidates_path or not os.path.exists(candidates_path):
        raise HTTPException(status_code=404, detail="Candidates not found for this project")

    import json
    with open(candidates_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
