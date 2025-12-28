"""Health check and root routes."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
def root():
    """Root endpoint - health check."""
    return {
        "message": "Azure DevOps Automation API running",
        "status": "healthy",
        "version": "1.0.0"
    }


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Azure DevOps Automation"
    }
