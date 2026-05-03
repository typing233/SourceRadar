import json
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, Date, UniqueConstraint, JSON
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    receive_digest = Column(Boolean, default=True)
    llm_base_url = Column(String(500), nullable=True)
    llm_api_key = Column(String(500), nullable=True)
    llm_model_name = Column(String(100), nullable=True)
    llm_embedding_model = Column(String(100), nullable=True)

    user_tags = relationship("UserTag", back_populates="user", cascade="all, delete-orphan")
    digests = relationship("Digest", back_populates="user", cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=True)
    embedding = Column(JSON, nullable=True)

    user_tags = relationship("UserTag", back_populates="tag", cascade="all, delete-orphan")


class UserTag(Base):
    __tablename__ = "user_tags"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

    user = relationship("User", back_populates="user_tags")
    tag = relationship("Tag", back_populates="user_tags")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    description = Column(Text, default="")
    source = Column(String(20), nullable=False)  # github / hn / ph
    raw_tags = Column(Text, default="[]")  # JSON string list
    semantic_tags = Column(Text, default="[]")  # Semantically generated tags
    category = Column(String(100), nullable=True)
    embedding = Column(JSON, nullable=True)
    score = Column(Float, default=0.0)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime, nullable=True)

    digest_items = relationship("DigestItem", back_populates="item")

    def get_raw_tags(self) -> List[str]:
        try:
            return json.loads(self.raw_tags or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    def get_semantic_tags(self) -> List[str]:
        try:
            return json.loads(self.semantic_tags or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    def set_semantic_tags(self, tags: List[str]):
        self.semantic_tags = json.dumps(tags)

    def get_all_tags(self) -> List[str]:
        raw = self.get_raw_tags()
        semantic = self.get_semantic_tags()
        return list(set(raw + semantic))


class Digest(Base):
    __tablename__ = "digests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="digests")
    digest_items = relationship("DigestItem", back_populates="digest", cascade="all, delete-orphan")


class DigestItem(Base):
    __tablename__ = "digest_items"

    id = Column(Integer, primary_key=True, index=True)
    digest_id = Column(Integer, ForeignKey("digests.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    match_score = Column(Float, default=0.0)

    digest = relationship("Digest", back_populates="digest_items")
    item = relationship("Item", back_populates="digest_items")
