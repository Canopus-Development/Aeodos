from typing import Dict, Any
from datetime import datetime, timedelta
import json
import logging
from security import SecurityConfig

logger = logging.getLogger(__name__)

class UsageTracker:
    @classmethod
    async def get_detailed_metrics(cls, api_key: str) -> Dict[str, Any]:
        """Get detailed API usage metrics"""
        redis_client = SecurityConfig.redis_client
        
        # Get usage patterns
        usage_pattern = f"usage:{api_key}:*"
        all_keys = redis_client.keys(usage_pattern)
        
        # Collect metrics
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0)
        
        metrics = {
            "period_start": period_start.isoformat(),
            "period_end": (period_start + timedelta(days=30)).isoformat(),
            "total_requests": 0,
            "hourly_usage": 0,
            "daily_usage": 0,
            "monthly_usage": 0,
            "endpoint_usage": {},
            "quota": 1000  # Default quota
        }
        
        # Calculate usage
        for key in all_keys:
            count = int(redis_client.get(key) or 0)
            metrics["total_requests"] += count
            
            # Parse endpoint from key
            endpoint = key.decode().split(":")[-1]
            metrics["endpoint_usage"][endpoint] = count
        
        return metrics

async def track_project_generation(
    user_id: int,
    project_id: str,
    tier: str
) -> None:
    """Track project generation metrics"""
    try:
        redis_client = SecurityConfig.redis_client
        key = f"project_metrics:{user_id}:{project_id}"
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "tier": tier,
            "status": "started"
        }
        
        redis_client.setex(
            key,
            timedelta(days=30),
            json.dumps(metrics)
        )
        
    except Exception as e:
        logger.error(f"Failed to track project generation: {str(e)}")

async def track_generation_metrics(
    api_key: str,
    generation_type: str,
    duration: float
) -> None:
    """Track code generation metrics"""
    try:
        redis_client = SecurityConfig.redis_client
        key = f"generation_metrics:{api_key}:{generation_type}"
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "duration": duration,
            "type": generation_type
        }
        
        redis_client.setex(
            key,
            timedelta(days=7),
            json.dumps(metrics)
        )
        
    except Exception as e:
        logger.error(f"Failed to track generation metrics: {str(e)}")
