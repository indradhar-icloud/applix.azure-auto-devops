"""Event schemas for data transfer."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class EventBase(BaseModel):
    """Base event schema."""
    event_type: str = Field(..., min_length=1, max_length=100)
    data: Dict[str, Any]


class EventCreate(EventBase):
    """Schema for creating an event."""
    pass


class EventResponse(BaseModel):
    """Schema for event API response."""
    id: int
    event_type: str
    status: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class EventInDB(EventBase):
    """Schema for event in database."""
    id: int
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}
