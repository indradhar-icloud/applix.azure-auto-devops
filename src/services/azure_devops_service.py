"""Azure DevOps integration service."""

import requests
from typing import List, Dict, Any, Optional

from src.core.config import get_settings
from src.core.constants import AzureDevOpsConstants, TaskTemplates
from src.utils import (
    create_auth_header,
    build_work_item_url,
    create_work_item_patch,
    create_parent_link_patch,
    get_logger
)

logger = get_logger(__name__)
settings = get_settings()


class AzureDevOpsService:
    """
    Service for Azure DevOps API integration.
    Implements Single Responsibility Principle - handles only Azure DevOps operations.
    """
    
    def __init__(self):
        """Initialize Azure DevOps service."""
        self.org = settings.AZURE_DEVOPS_ORG
        self.project = settings.AZURE_DEVOPS_PROJECT
        self.pat = settings.AZURE_DEVOPS_PAT
        self.headers = create_auth_header(self.pat) if self.pat else {}
    
    def create_task(
        self,
        title: str,
        area_path: str,
        iteration_path: str
    ) -> Optional[int]:
        """
        Create a task in Azure DevOps.
        
        Args:
            title: Task title
            area_path: Area path
            iteration_path: Iteration path
            
        Returns:
            Task ID if successful, None otherwise
        """
        url = build_work_item_url(
            self.org,
            self.project,
            AzureDevOpsConstants.WORK_ITEM_TYPE_TASK
        )
        
        task_data = create_work_item_patch(title, area_path, iteration_path)
        
        try:
            response = requests.post(url, json=task_data, headers=self.headers)
            
            logger.info(f"Azure API Response: Status={response.status_code}")
            
            # Accept 200, 201, 203 as success
            if response.status_code in [200, 201, 203]:
                task_id = response.json()['id']
                logger.info(f"✓ Created task #{task_id}: {title}")
                return task_id
            else:
                logger.error(f"✗ Failed to create task: {response.status_code} - {response.text[:200]}")
                logger.error(f"  URL: {url}")
                return None
        except Exception as e:
            logger.error(f"✗ Exception creating task: {e}", exc_info=True)
            return None
    
    def link_task_to_story(self, task_id: int, story_id: int) -> bool:
        """
        Link a task to its parent story.
        
        Args:
            task_id: Task ID
            story_id: Parent story ID
            
        Returns:
            True if successful, False otherwise
        """
        url = build_work_item_url(
            self.org,
            self.project,
            AzureDevOpsConstants.WORK_ITEM_TYPE_TASK,
            work_item_id=task_id
        )
        
        link_data = create_parent_link_patch(self.org, self.project, story_id)
        
        try:
            response = requests.patch(url, json=link_data, headers=self.headers)
            
            if response.status_code == 200:
                logger.info(f"  └─ Linked task #{task_id} to story #{story_id}")
                return True
            else:
                logger.warning(
                    f"  ⚠️ Linking failed (status {response.status_code}): {response.text[:100]}"
                )
                logger.warning(
                    f"  ℹ️ Task created but not linked. Verify story #{story_id} exists in Azure DevOps"
                )
                return False
        except Exception as e:
            logger.error(f"  ✗ Exception linking task: {e}")
            return False
    
    def create_subtasks_for_story(
        self,
        story_id: int,
        area_path: str,
        iteration_path: str,
        tasks: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create standard subtasks for a user story.
        
        Args:
            story_id: Parent story ID
            area_path: Area path
            iteration_path: Iteration path
            tasks: Optional custom task list (uses standard template if None)
            
        Returns:
            Dictionary with created task count and IDs
        """
        tasks = tasks or TaskTemplates.STANDARD_TASKS
        created_tasks = []
        
        for task_title in tasks:
            task_id = self.create_task(task_title, area_path, iteration_path)
            
            if task_id:
                created_tasks.append(task_id)
                self.link_task_to_story(task_id, story_id)
            else:
                logger.error(f"Failed to create task: {task_title}")
                raise Exception(f"Task creation failed for: {task_title}")
        
        return {
            "story_id": story_id,
            "tasks_created": len(created_tasks),
            "task_ids": created_tasks
        }
