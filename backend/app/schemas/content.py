from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ContentResponse(BaseModel):
    id: int
    title: str
    description: str
    url: str
    source: str
    tags: List[str]
    score: int
    published_at: Optional[datetime]
    created_at: datetime
    match_score: Optional[float] = None

    class Config:
        from_attributes = True


class FeedResponse(BaseModel):
    items: List[ContentResponse]
    total: int
    page: int
    size: int
    pages: int
