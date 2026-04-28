from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime
    is_active: bool
    receive_digest: bool

    model_config = {"from_attributes": True}


# ── Tags ──────────────────────────────────────────────────────────────────────

class TagOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class UserTagsUpdate(BaseModel):
    tags: list[str]


class UserSettingsUpdate(BaseModel):
    receive_digest: Optional[bool] = None
    tags: Optional[list[str]] = None


# ── Items ─────────────────────────────────────────────────────────────────────

class ItemOut(BaseModel):
    id: int
    title: str
    url: str
    description: str
    source: str
    raw_tags: list[str]
    score: float
    published_at: Optional[datetime]
    created_at: datetime
    match_score: float = 0.0

    model_config = {"from_attributes": True}


class FeedResponse(BaseModel):
    items: list[ItemOut]
    total: int
    page: int


# ── Digest ────────────────────────────────────────────────────────────────────

class DigestItemOut(BaseModel):
    id: int
    item_id: int
    match_score: float
    title: str
    url: str
    description: str
    source: str
    raw_tags: list[str]
    published_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DigestOut(BaseModel):
    id: int
    user_id: int
    week_start: datetime
    created_at: datetime
    sent_at: Optional[datetime]
    items: list[DigestItemOut]

    model_config = {"from_attributes": True}
