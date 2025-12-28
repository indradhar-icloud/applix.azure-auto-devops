"""Event queue service for publishing and processing events."""

import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from src.repositories import EventRepository
from src.core.constants import EventStatus
from src.utils import get_logger

logger = get_logger(__name__)


class EventQueueService:
    """
    Service for managing event queue operations.
    Implements Single Responsibility Principle - handles only event queue logic.
    """
    
    def __init__(self, db: Session):
        """
        Initialize event queue service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.event_repo = EventRepository(db)
    
    def publish_event(self, event_type: str, data: Dict[str, Any]) -> int:
        """
        Publish a new event to the queue.
        
        Args:
            event_type: Type of event
            data: Event data
            
        Returns:
            Event ID
        """
        event = self.event_repo.create(
            event_type=event_type,
            data=json.dumps(data),
            status=EventStatus.PENDING.value
        )
        logger.info(f"Published event #{event.id} of type '{event_type}'")
        return event.id
    
    def get_pending_events(self) -> List:
        """
        Get all pending events.
        
        Returns:
            List of pending events
        """
        return self.event_repo.get_pending_events()
    
    def mark_processing(self, event_id: int) -> None:
        """Mark an event as processing."""
        self.event_repo.mark_processing(event_id)
        logger.debug(f"Event #{event_id} marked as processing")
    
    def mark_completed(self, event_id: int, result: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark an event as completed.
        
        Args:
            event_id: Event ID
            result: Optional result data
        """
        result_json = json.dumps(result) if result else None
        self.event_repo.mark_completed(event_id, result_json)
        logger.info(f"Event #{event_id} completed successfully")
    
    def mark_failed(self, event_id: int, error: str) -> None:
        """
        Mark an event as failed.
        
        Args:
            event_id: Event ID
            error: Error message
        """
        self.event_repo.mark_failed(event_id, error)
        logger.error(f"Event #{event_id} failed: {error}")


class EventQueueServiceSingleton:
    """Singleton wrapper for EventQueueService."""
    
    _instance: Optional[EventQueueService] = None
    
    @classmethod
    def get_instance(cls, db: Optional[Session] = None) -> EventQueueService:
        """Get or create singleton instance."""
        if cls._instance is None:
            if db is None:
                from src.core.database import SessionLocal
                db = SessionLocal()
            cls._instance = EventQueueService(db)
        return cls._instance
