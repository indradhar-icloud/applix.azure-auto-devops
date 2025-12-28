"""SQLAlchemy database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Event(Base):
    """Event model for event queue."""
    
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(100), index=True, nullable=False)
    data = Column(Text, nullable=False)
    status = Column(String(50), default="pending", index=True, nullable=False)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Event(id={self.id}, type={self.event_type}, status={self.status})>"


class UserStoryRecord(Base):
    """User story model."""
    
    __tablename__ = "user_stories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    azure_story_id = Column(Integer, unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    area_path = Column(String(255), nullable=True)
    iteration_path = Column(String(255), nullable=True)
    status = Column(String(50), default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<UserStoryRecord(id={self.id}, azure_id={self.azure_story_id}, title={self.title})>"
