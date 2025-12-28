"""User story repository for database operations."""

from typing import Optional
from sqlalchemy.orm import Session

from src.core.models import UserStoryRecord


class UserStoryRepository:
    """Repository for UserStory database operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def create_story(
        self,
        azure_story_id: int,
        title: str,
        area_path: str = None,
        iteration_path: str = None,
        status: str = "pending"
    ) -> UserStoryRecord:
        """Create a new user story."""
        story = UserStoryRecord(
            azure_story_id=azure_story_id,
            title=title,
            area_path=area_path,
            iteration_path=iteration_path,
            status=status
        )
        self.db.add(story)
        self.db.commit()
        self.db.refresh(story)
        return story
    
    def get_by_azure_id(self, azure_story_id: int) -> Optional[UserStoryRecord]:
        """Get user story by Azure DevOps ID."""
        return self.db.query(UserStoryRecord).filter(
            UserStoryRecord.azure_story_id == azure_story_id
        ).first()
    
    def update_status(self, azure_story_id: int, status: str) -> Optional[UserStoryRecord]:
        """Update user story status."""
        story = self.get_by_azure_id(azure_story_id)
        if story:
            story.status = status
            self.db.commit()
            self.db.refresh(story)
        return story
