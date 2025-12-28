"""Application constants and enums."""

from enum import Enum


class EventStatus(str, Enum):
    """Event processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class StoryStatus(str, Enum):
    """User story status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class EventType(str, Enum):
    """Event types."""
    USER_STORY_CREATED = "user_story_created"
    USER_STORY_COMPLETED = "user_story_completed"


class AzureDevOpsConstants:
    """Azure DevOps API constants."""
    API_VERSION = "7.0"
    CONTENT_TYPE = "application/json-patch+json"
    WORK_ITEM_TYPE_TASK = "Task"
    
    # Default Azure DevOps paths
    DEFAULT_AREA_PATH = "Devops-Automation"
    DEFAULT_ITERATION_PATH = "Devops-Automation"
    
    # Relation types
    HIERARCHY_REVERSE_LINK = "System.LinkTypes.Hierarchy-Reverse"


class TaskTemplates:
    """Standard task templates for user stories."""
    STANDARD_TASKS = [
        "1. Requirements & Grooming",
        "2. Design & Approach",
        "3. Implementation",
        "4. Testing & QA",
        "5. Deployment & Documentation"
    ]


class WorkerConfig:
    """Worker daemon configuration."""
    DEFAULT_POLL_INTERVAL = 3  # seconds
    LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
    LOG_DATE_FORMAT = '%H:%M:%S'
