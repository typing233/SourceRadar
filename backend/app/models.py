import json
from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, Date, UniqueConstraint
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

    user_tags = relationship("UserTag", back_populates="user", cascade="all, delete-orphan")
    digests = relationship("Digest", back_populates="user", cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

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
    score = Column(Float, default=0.0)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    digest_items = relationship("DigestItem", back_populates="item")

    def get_raw_tags(self) -> list[str]:
        try:
            return json.loads(self.raw_tags or "[]")
        except (json.JSONDecodeError, TypeError):
            return []


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
