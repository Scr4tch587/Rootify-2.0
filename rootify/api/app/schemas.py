from pydantic import BaseModel
from datetime import datetime

class ArtistCreate(BaseModel):
    name: str

class ArtistOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

class EvidenceSectionOut(BaseModel):
    id: int
    source : str
    keyword: str | None
    section_path: str
    text: str
    is_fallback: bool
    created_at: datetime

    class Config:
        from_attributes = True

class InfluenceCandidateOut(BaseModel):
    influence_artist: str
    pattern_type: str
    section_path: str
    snippet: str

class InfluenceEvidenceOut(BaseModel):
    section_path: str
    snippet: str
    pattern_type: str

class InfluenceOut(BaseModel):
    influence_artist: str
    score: float
    evidence_count: int
    evidence: list[InfluenceEvidenceOut]