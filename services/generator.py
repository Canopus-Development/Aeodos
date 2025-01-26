from typing import Dict, Any
from fastapi import HTTPException
import logging

from services.ai import WebsiteGenerationService, DocumentationService, DebugService

logger = logging.getLogger(__name__)

def get_generation_service(generation_type: str) -> Any:
    """Get appropriate generation service based on type"""
    services = {
        "frontend": WebsiteGenerationService(),
        "backend": WebsiteGenerationService(),
        "debug": DebugService(),
        "docs": DocumentationService()
    }
    
    service = services.get(generation_type)
    if not service:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid generation type: {generation_type}"
        )
    
    return service
