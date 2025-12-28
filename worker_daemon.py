"""
Worker daemon for processing events from the queue.
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.database import init_db, get_db_context
from src.core.config import get_settings
from src.core.constants import WorkerConfig
from src.services import EventQueueService
from src.services.event_processor import EventProcessor
from src.utils import setup_logger

# Initialize logger
logger = setup_logger(__name__)
settings = get_settings()


class WorkerDaemon:
    """
    Worker daemon for processing events.
    Implements Single Responsibility Principle - only handles worker lifecycle.
    """
    
    def __init__(self, poll_interval: int = WorkerConfig.DEFAULT_POLL_INTERVAL):
        """
        Initialize worker daemon.
        
        Args:
            poll_interval: Time in seconds between polling cycles
        """
        self.poll_interval = poll_interval
        self.running = False
    
    def start(self) -> None:
        """Start the worker daemon."""
        logger.info("=" * 70)
        logger.info("EVENT-DRIVEN WORKER DAEMON STARTED")
        logger.info(f"Polling interval: {self.poll_interval}s")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info("=" * 70)
        
        # Initialize database
        init_db()
        logger.info("✓ Database initialized")
        
        self.running = True
        
        try:
            self._run_loop()
        except KeyboardInterrupt:
            logger.info("\nWorker daemon stopped by user")
        except Exception as e:
            logger.error(f"Worker daemon error: {e}", exc_info=True)
            raise
        finally:
            self.running = False
    
    def _run_loop(self) -> None:
        """Main worker loop."""
        while self.running:
            try:
                with get_db_context() as db:
                    # Create services with dependency injection
                    event_queue = EventQueueService(db)
                    processor = EventProcessor(event_queue, db)
                    
                    # Get pending events
                    pending_events = event_queue.get_pending_events()
                    
                    if pending_events:
                        logger.info(f"Found {len(pending_events)} pending event(s)")
                        
                        for event in pending_events:
                            processor.process_event(event)
                
                # Sleep between polling cycles
                time.sleep(self.poll_interval)
            
            except Exception as e:
                logger.error(f"Error in worker loop: {e}", exc_info=True)
                time.sleep(self.poll_interval)
    
    def stop(self) -> None:
        """Stop the worker daemon."""
        self.running = False
        logger.info("Worker daemon stopping...")


def main():
    """Main entry point."""
    worker = WorkerDaemon(poll_interval=WorkerConfig.DEFAULT_POLL_INTERVAL)
    worker.start()


if __name__ == "__main__":
    main()
