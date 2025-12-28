"""Event repository for database operations."""

from typing import List
from sqlalchemy.orm import Session

from src.core.models import Event
from src.core.constants import EventStatus


class EventRepository:
    """Repository for Event database operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def create(self, event_type: str, data: str, status: str) -> Event:
        """Create a new event."""
        event = Event(event_type=event_type, data=data, status=status)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def get_pending_events(self) -> List[Event]:
        """Get all pending events."""
        return self.db.query(Event).filter(
            Event.status == EventStatus.PENDING.value
        ).all()
    
    def mark_processing(self, event_id: int) -> None:
        """Mark event as processing."""
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if event:
            event.status = EventStatus.PROCESSING.value
            self.db.commit()
    
    def mark_completed(self, event_id: int, result: str = None) -> None:
        """Mark event as completed."""
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if event:
            event.status = EventStatus.COMPLETED.value
            event.result = result
            self.db.commit()
    
    def mark_failed(self, event_id: int, error: str) -> None:
        """Mark event as failed."""
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if event:
            event.status = EventStatus.FAILED.value
            event.error_message = error
            self.db.commit()
