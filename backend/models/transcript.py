from typing import List, Optional
from pydantic import BaseModel, Field

class TranscriptSegment(BaseModel):
    id: int
    start: float = Field(..., description="Start timestamp in seconds")
    end: float = Field(..., description="End timestamp in seconds")
    text: str = Field(..., description="Transcribed text content")

class TranscriptData(BaseModel):
    project_id: str
    language: str = Field("en", description="Detected language code")
    duration_seconds: Optional[float] = Field(None, description="Total audio duration in seconds")
    segments: List[TranscriptSegment] = Field(default_factory=list)
