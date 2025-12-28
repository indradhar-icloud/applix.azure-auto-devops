"""Event processor for handling different event types."""

import json
from typing import Dict, Any
from sqlalchemy.orm import Session

from src.services import AzureDevOpsService, EventQueueService, UserStoryService
from src.core.constants import EventType, AzureDevOpsConstants, StoryStatus
from src.utils import get_logger

logger = get_logger(__name__)


class EventProcessor:
    """
    Processes events from the event queue.
    Implements Single Responsibility Principle and Open/Closed Principle.
    """
    
    def __init__(self, event_queue: EventQueueService, db: Session):
        """
        Initialize event processor.
        
        Args:
            event_queue: Event queue service instance
            db: Database session
        """
        self.event_queue = event_queue
        self.azure_service = AzureDevOpsService()
        self.story_service = UserStoryService(db)
    
    def process_event(self, event) -> None:
        """
        Process a single event.
        
        Args:
            event: Event object from database
        """
        event_id = event.id
        event_type = event.event_type
        event_data = json.loads(event.data) if isinstance(event.data, str) else event.data
        
        try:
            self.event_queue.mark_processing(event_id)
            logger.info(f"[Event {event_id}] Processing: {event_type}")
            
            # Dispatch to appropriate handler
            if event_type == EventType.USER_STORY_CREATED.value:
                result = self._process_user_story_created(event_id, event_data)
                self.event_queue.mark_completed(event_id, result)
            elif event_type == EventType.USER_STORY_COMPLETED.value:
                # Just mark as completed, no further processing needed
                logger.info(f"[Event {event_id}] Completion event recorded")
                self.event_queue.mark_completed(event_id, {"status": "recorded"})
            else:
                raise Exception(f"Unknown event type: {event_type}")
        
        except Exception as e:
            logger.error(f"[Event {event_id}] ✗ Failed: {e}")
            self.event_queue.mark_failed(event_id, str(e))
    
    def _process_user_story_created(self, event_id: int, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user story created event.
        
        Args:
            event_id: Event ID
            story_data: Story data from event
            
        Returns:
            Result dictionary with created task information
        """
        story_id = story_data['story_id']
        area_path = story_data.get('area_path') or AzureDevOpsConstants.DEFAULT_AREA_PATH
        iteration_path = story_data.get('iteration_path') or AzureDevOpsConstants.DEFAULT_ITERATION_PATH
        
        logger.info(f"[Event {event_id}] Processing Story #{story_id}")
        
        # Create subtasks using Azure DevOps service
        result = self.azure_service.create_subtasks_for_story(
            story_id=story_id,
            area_path=area_path,
            iteration_path=iteration_path
        )
        
        # Update story status to completed
        self.story_service.update_story_status(story_id, StoryStatus.COMPLETED.value)
        logger.info(f"[Event {event_id}] Updated story #{story_id} status to completed")
        
        # Publish completion event
        self.event_queue.publish_event(
            EventType.USER_STORY_COMPLETED.value,
            result
        )
        
        logger.info(
            f"[Event {event_id}] ✓ Completed: {result['tasks_created']} subtasks created"
        )
        
        return result
