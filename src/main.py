"""
FastAPI application entry point.
"""

import threading
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.config import get_settings
from src.core.database import init_db
from src.api import api_router
from src.utils import setup_logger

settings = get_settings()
logger = setup_logger(__name__)

# Worker daemon reference (global for lifespan management)
worker_thread = None
worker_daemon = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    global worker_thread, worker_daemon
    
    # Startup
    logger.info("=" * 70)
    logger.info("STARTING APPLICATION")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("=" * 70)
    
    init_db()
    logger.info("✓ Database initialized")
    logger.info("✓ Event queue ready")
    
    # Start worker daemon in background thread
    auto_start = settings.AUTO_START_WORKER
    if auto_start:
        from worker_daemon import WorkerDaemon
        from src.core.constants import WorkerConfig
        
        worker_daemon = WorkerDaemon(poll_interval=WorkerConfig.DEFAULT_POLL_INTERVAL)
        worker_thread = threading.Thread(target=worker_daemon.start, daemon=True)
        worker_thread.start()
        logger.info("✓ Worker daemon started in background")
    else:
        logger.info("⊘ Worker daemon auto-start disabled (use: AUTO_START_WORKER=true)")
    
    logger.info("✓ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("=" * 70)
    logger.info("SHUTTING DOWN APPLICATION")
    logger.info("=" * 70)
    
    # Stop worker daemon
    if worker_daemon:
        worker_daemon.stop()
        if worker_thread and worker_thread.is_alive():
            worker_thread.join(timeout=5)
        logger.info("✓ Worker daemon stopped")
    
    logger.info("✓ Shutdown complete")


def create_app() -> FastAPI:
    """
    Application factory pattern.
    Creates and configures the FastAPI application.
    """
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Include all API routes
    app.include_router(api_router)
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.is_development
    )
