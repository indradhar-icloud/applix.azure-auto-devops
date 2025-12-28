"""User story service for business logic."""

from typing import Dict, Any
from sqlalchemy.orm import Session

from src.repositories import UserStoryRepository
from src.services.event_queue_service import EventQueueService
from src.core.constants import EventType, StoryStatus
from src.utils import get_logger

logger = get_logger(__name__)


class UserStoryService:
    """
    Service for user story business logic.
    Implements Single Responsibility Principle - handles only user story operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize user story service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.story_repo = UserStoryRepository(db)
        self.event_queue = EventQueueService(db)
    
    def create_user_story(
        self,
        story_id: int,
        title: str,
        area_path: str = None,
        iteration_path: str = None
    ) -> Dict[str, Any]:
        """
        Create a user story and publish creation event.
        
        Args:
            story_id: Azure DevOps story ID
            title: Story title
            area_path: Area path
            iteration_path: Iteration path
            
        Returns:
            Response dictionary with status and event info
        """
        logger.info(f"Creating user story #{story_id}: {title}")
        
        # Store in database
        story = self.story_repo.create_story(
            azure_story_id=story_id,
            title=title,
            area_path=area_path,
            iteration_path=iteration_path,
            status=StoryStatus.PENDING.value
        )
        logger.info(f"Stored story #{story_id} in database")
        
        # Publish event
        event_id = self.event_queue.publish_event(
            EventType.USER_STORY_CREATED.value,
            {
                "story_id": story_id,
                "title": title,
                "area_path": area_path,
                "iteration_path": iteration_path
            }
        )
        logger.info(f"Published event #{event_id} for story #{story_id}")
        
        return {
            "status": "accepted",
            "message": f"Story #{story_id} received. Subtasks will be created asynchronously.",
            "story_id": story_id,
            "event_id": event_id
        }
    
    def get_user_story(self, azure_story_id: int):
        """Get user story by Azure ID."""
        return self.story_repo.get_by_azure_id(azure_story_id)
    
    def update_story_status(self, azure_story_id: int, status: str):
        """Update user story status."""
        return self.story_repo.update_status(azure_story_id, status)
