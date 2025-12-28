"""User story schemas for data transfer."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserStoryBase(BaseModel):
    """Base user story schema."""
    title: str = Field(..., min_length=1, max_length=500)
    area_path: Optional[str] = Field(None, max_length=255)
    iteration_path: Optional[str] = Field(None, max_length=255)


class UserStoryCreate(UserStoryBase):
    """Schema for creating a user story."""
    id: int = Field(..., gt=0, description="Azure DevOps story ID")


class UserStoryResponse(BaseModel):
    """Schema for user story API response."""
    status: str
    message: str
    story_id: int
    event_id: int
    
    model_config = {"from_attributes": True}


class UserStoryInDB(UserStoryBase):
    """Schema for user story in database."""
    id: int
    azure_story_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
