"""User story API routes."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

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
