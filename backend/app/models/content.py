from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from ..database import Base


class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    url = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, nullable=False)  # github, hackernews, producthunt
    tags = Column(JSON, default=list)
    score = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
