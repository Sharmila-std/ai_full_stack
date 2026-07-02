import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .database import Base

class InfluencerModel(Base):
    __tablename__ = "influencers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)
    profile_url = Column(Text, unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    followers = Column(String(100), nullable=True, default="Not Available")
    match_score = Column(Integer, nullable=False, default=0)
    match_reason = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SearchHistoryModel(Base):
    __tablename__ = "search_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt = Column(Text, nullable=False)
    platforms = Column(Text, nullable=False)  # Stored as comma-separated values
    created_at = Column(DateTime(timezone=True), server_default=func.now())

