from typing import List, Optional
from pydantic import BaseModel, Field

class ClipScores(BaseModel):
    hook: float = Field(..., ge=0, le=10)
    standalone_context: float = Field(..., ge=0, le=10)
    message_completeness: float = Field(..., ge=0, le=10)
    emotional_impact: float = Field(..., ge=0, le=10)
    curiosity: float = Field(..., ge=0, le=10)
    shareability: float = Field(..., ge=0, le=10)

class ClipCandidate(BaseModel):
    candidate_id: str
    project_id: str
    start: float = Field(..., description="Start timestamp in seconds")
    end: float = Field(..., description="End timestamp in seconds")
    duration: float = Field(..., description="Duration in seconds")
    title: str = Field(..., description="Catchy title for the reel")
    hook: str = Field(..., description="First 3-5 seconds opening hook sentence")
    reason: str = Field(..., description="Why this clip was selected")
    scores: ClipScores
    final_score: float = Field(..., ge=0, le=100, description="Weighted final clip potential score out of 100")
