from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from uuid import UUID

# Influencer schemas
class InfluencerBase(BaseModel):
    name: str
    username: str
    platform: str
    profile_url: str
    bio: Optional[str] = None
    followers: Optional[str] = "Not Available"
    match_score: int = 0
    match_reason: Optional[str] = None

class InfluencerCreate(InfluencerBase):
    pass

class InfluencerResponse(InfluencerBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Search request/response schemas
class SearchRequest(BaseModel):
    prompt: str
    platforms: List[str]

class SearchResultItem(InfluencerBase):
    pass

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
