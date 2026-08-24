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
