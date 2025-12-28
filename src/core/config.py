"""Application configuration management."""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = ConfigDict(env_file=".env", case_sensitive=True)
    
    # Azure DevOps configuration
    AZURE_DEVOPS_ORG: Optional[str] = None
    AZURE_DEVOPS_PROJECT: Optional[str] = None
    AZURE_DEVOPS_PAT: Optional[str] = None
    
    # Database settings
    DATABASE_URL: str = None
    
    # Application settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    AUTO_START_WORKER: bool = True
    
    # API settings
    API_TITLE: str = "Azure DevOps Automation - Event-Driven"
    API_DESCRIPTION: str = "Async user story processing with event queue"
    API_VERSION: str = "1.0.0"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
