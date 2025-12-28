"""Azure DevOps API utilities."""

import base64
from typing import Dict, Optional


def create_auth_header(pat: str) -> Dict[str, str]:
    """
    Create authorization header for Azure DevOps API.
    
    Args:
        pat: Personal Access Token
        
    Returns:
        Dictionary with authorization headers
    """
    auth_string = base64.b64encode(f":{pat}".encode()).decode()
    return {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/json-patch+json"
    }


def build_work_item_url(
    org: str,
    project: str,
    work_item_type: str,
    work_item_id: Optional[int] = None,
    api_version: str = "7.0"
) -> str:
    """
    Build Azure DevOps work item API URL.
    
    Args:
        org: Organization name
        project: Project name
        work_item_type: Type of work item (Task, Story, etc.)
        work_item_id: Optional work item ID for updates
        api_version: API version
        
    Returns:
        Complete API URL
    """
    base_url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems"
    
    if work_item_id:
        return f"{base_url}/{work_item_id}?api-version={api_version}"
    else:
        return f"{base_url}/${work_item_type}?api-version={api_version}"


def create_work_item_patch(
    title: str,
    area_path: str,
    iteration_path: str
) -> list:
    """
    Create work item patch data for Azure DevOps API.
    
    Args:
        title: Work item title
        area_path: Area path
        iteration_path: Iteration path
        
    Returns:
        List of patch operations
    """
    return [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/System.AreaPath", "value": area_path},
        {"op": "add", "path": "/fields/System.IterationPath", "value": iteration_path},
    ]


def create_parent_link_patch(org: str, project: str, parent_id: int) -> list:
    """
    Create patch data for linking work item to parent.
    
    Args:
        org: Organization name
        project: Project name
        parent_id: Parent work item ID
        
    Returns:
        List of patch operations for creating parent link
    """
    return [{
        "op": "add",
        "path": "/relations/-",
        "value": {
            "rel": "System.LinkTypes.Hierarchy-Reverse",
            "url": f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{parent_id}"
        }
    }]
