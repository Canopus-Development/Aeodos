from typing import Dict, Any
import logging
from sqlalchemy import text
from redis.exceptions import RedisError
from azure.core.exceptions import AzureError
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

from database import get_db
from security import SecurityConfig
from services.ai import AIConfig

logger = logging.getLogger(__name__)

def check_database_health() -> Dict[str, Any]:
    """Check database connectivity and health"""
    try:
        db = next(get_db())
        db.execute(text('SELECT 1'))
        return {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }

def check_redis_health() -> Dict[str, Any]:
    """Check Redis connectivity and health"""
    try:
        SecurityConfig.redis_client.ping()
        return {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except RedisError as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }

def check_ai_models_health() -> Dict[str, Any]:
    """Check AI models availability and health"""
    try:
        client = ChatCompletionsClient(
            endpoint=AIConfig.ENDPOINT,
            credential=AzureKeyCredential(AIConfig.TOKEN)
        )
        
        # Check each model's availability
        model_status = {}
        for model_type, model_name in AIConfig.MODELS.items():
            try:
                # Simple model check (can be enhanced based on specific requirements)
                client.get_model_info(model_name)
                model_status[model_type] = "available"
            except AzureError as e:
                model_status[model_type] = f"unavailable: {str(e)}"
        
        return {
            "status": "healthy" if all(status == "available" for status in model_status.values()) else "degraded",
            "models": model_status
        }
    except Exception as e:
        logger.error(f"AI models health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }
