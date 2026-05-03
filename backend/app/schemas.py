from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, EmailStr, HttpUrl


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
    llm_base_url: Optional[str] = None
    llm_model_name: Optional[str] = None
    llm_embedding_model: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Tags ──────────────────────────────────────────────────────────────────────

class TagOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None

    model_config = {"from_attributes": True}


class UserTagsUpdate(BaseModel):
    tags: list[str]


class UserSettingsUpdate(BaseModel):
    receive_digest: Optional[bool] = None
    tags: Optional[list[str]] = None


# ── LLM Configuration ─────────────────────────────────────────────────────────

class LLMConfigUpdate(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    embedding_model: Optional[str] = None


class LLMConfigOut(BaseModel):
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    embedding_model: Optional[str] = None
    configured: bool = False

    model_config = {"from_attributes": True}


class LLMConnectionTest(BaseModel):
    success: bool
    message: str


# ── Items ─────────────────────────────────────────────────────────────────────

class ItemOut(BaseModel):
    id: int
    title: str
    url: str
    description: str
    source: str
    raw_tags: list[str]
    semantic_tags: list[str]
    category: Optional[str] = None
    score: float
    published_at: Optional[datetime]
    created_at: datetime
    analyzed_at: Optional[datetime] = None
    match_score: float = 0.0

    model_config = {"from_attributes": True}


class FeedResponse(BaseModel):
    items: list[ItemOut]
    total: int
    page: int


# ── 3D Topology / Clustering ──────────────────────────────────────────────────

class ClusterNode(BaseModel):
    id: int
    title: str
    url: str
    source: str
    category: Optional[str] = None
    tags: list[str]
    match_score: float = 0.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    size: float = 1.0


class ClusterLink(BaseModel):
    source: int
    target: int
    strength: float


class TopologyResponse(BaseModel):
    nodes: list[ClusterNode]
    links: list[ClusterLink]
    categories: list[str]
    total_nodes: int


class ClusterResponse(BaseModel):
    category: str
    items: list[ItemOut]
    count: int


class ClusterListResponse(BaseModel):
    clusters: list[ClusterResponse]
    total_items: int
    categories: list[str]


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
