"""User story API routes."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.core.database import get_db
from src.schemas import UserStoryCreate, UserStoryResponse
from src.services import UserStoryService
from src.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/userstory", tags=["User Stories"])


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=UserStoryResponse
)
def create_user_story(
    story: UserStoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user story and trigger async subtask creation.
    
    Args:
        story: User story data
        db: Database session (injected)
        
    Returns:
        Response with story and event information
    """
    try:
        logger.info(f"API Request: Creating user story #{story.id}: {story.title}")
        
        # Get service with dependency injection
        service = UserStoryService(db)
        
        # Create story and publish event
        result = service.create_user_story(
            story_id=story.id,
            title=story.title,
            area_path=story.area_path,
            iteration_path=story.iteration_path
        )
        
        return UserStoryResponse(**result)
    
    except Exception as e:
        logger.error(f"Error creating user story: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{story_id}")
def get_user_story(
    story_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user story by Azure DevOps ID.
    
    Args:
        story_id: Azure DevOps story ID
        db: Database session (injected)
        
    Returns:
        User story data
    """
    service = UserStoryService(db)
    story = service.get_user_story(story_id)
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story #{story_id} not found"
        )
    
    return story


@router.post("/webhook/azure")
def azure_webhook(
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Azure DevOps webhook endpoint for work item creation.
    Automatically creates subtasks when a User Story is created in Azure DevOps.
    
    Args:
        payload: Azure DevOps webhook payload
        db: Database session (injected)
        
    Returns:
        Confirmation response
    """
    try:
        logger.info("Azure webhook received")
        
        # Extract event type
        event_type = payload.get("eventType", "")
        
        # Only process work item creation events
        if "workitem.created" not in event_type:
            logger.info(f"Ignoring event type: {event_type}")
            return {"status": "ignored", "message": f"Event type {event_type} not processed"}
        
        # Extract work item details
        resource = payload.get("resource", {})
        work_item_id = resource.get("id")
        work_item_type = resource.get("workItemType", "")
        fields = resource.get("fields", {})
        
        # Only process User Stories
        if work_item_type != "User Story":
            logger.info(f"Ignoring work item type: {work_item_type}")
            return {"status": "ignored", "message": f"Work item type {work_item_type} not processed"}
        
        title = fields.get("System.Title", "")
        area_path = fields.get("System.AreaPath", "Devops-automation")
        iteration_path = fields.get("System.IterationPath", "Devops-automation")
        
        logger.info(f"Processing User Story #{work_item_id}: {title}")
        
        # Call create endpoint internally
        service = UserStoryService(db)
        result = service.create_user_story(
            story_id=work_item_id,
            title=title,
            area_path=area_path,
            iteration_path=iteration_path
        )
        
        logger.info(f"User Story #{work_item_id} processed successfully")
        
        return {
            "status": "accepted",
            "message": f"Story #{work_item_id} received. Subtasks will be created asynchronously.",
            "story_id": work_item_id,
            "event_id": result.get("event_id")
        }
    
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }
