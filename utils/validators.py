from typing import Dict, Any
from fastapi import HTTPException
import logging
from models.subscription import SubscriptionPlan

logger = logging.getLogger(__name__)

async def validate_project_request(data: Dict[str, Any]) -> bool:
    """Validate project generation request"""
    try:
        if not data.get("project_name"):
            raise ValueError("Project name is required")
            
        if len(data.get("description", "")) < 10:
            raise ValueError("Description must be at least 10 characters")
            
        if not data.get("frontend_config"):
            raise ValueError("Frontend configuration is required")
            
        if not data.get("backend_config"):
            raise ValueError("Backend configuration is required")
            
        return True
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Project validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Validation error")

async def validate_version_compatibility(version: str, generation_type: str) -> bool:
    """Validate API version compatibility"""
    supported_versions = {
        "frontend": ["v1", "v2"],
        "backend": ["v1"],
        "debug": ["v1"],
        "project": ["v1"]
    }
    
    if version not in supported_versions.get(generation_type, []):
        raise HTTPException(
            status_code=400,
            detail=f"Version {version} not supported for {generation_type}"
        )
    
    return True
