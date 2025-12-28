"""API routes aggregation."""

from fastapi import APIRouter
from src.api.routes import health, user_story

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router)
api_router.include_router(user_story.router)

__all__ = ["api_router"]
