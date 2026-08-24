from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ProjectStatus(str, Enum):
    CREATED = "CREATED"
    DOWNLOADING = "DOWNLOADING"
    DOWNLOADED = "DOWNLOADED"
    EXTRACTING_AUDIO = "EXTRACTING_AUDIO"
    AUDIO_EXTRACTED = "AUDIO_EXTRACTED"
    TRANSCRIBING = "TRANSCRIBING"
    TRANSCRIBED = "TRANSCRIBED"
    ANALYZING = "ANALYZING"
    ANALYZED = "ANALYZED"
    RANKING = "RANKING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    RENDERING = "RENDERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ProjectCreate(BaseModel):
    url_or_path: str = Field(..., description="YouTube URL or local video file path")
    title: Optional[str] = Field(None, description="Optional custom title for the project")

class ProjectResponse(BaseModel):
    project_id: str
    title: str
    source_url: str
    status: ProjectStatus
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    transcript_path: Optional[str] = None
    candidates_path: Optional[str] = None
    ranked_clips_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    created_at: str
