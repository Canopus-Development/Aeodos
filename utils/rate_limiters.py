from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from database import SubscriptionTier
from models.user import User
import redis
import json

class ProjectGenerationLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    async def check_limit(
        self,
        user: User,
        request: Request,
        db: Session
    ) -> bool:
        """
        Check if user can generate a project based on their subscription tier
        """
        current_time = datetime.utcnow()
        cache_key = f"project_generation:{user.id}"
        
        # Premium users have unlimited access
        if user.subscription_tier == SubscriptionTier.PREMIUM:
            await self._track_usage(user.id, current_time)
            return True
            
        # Basic users are limited to 1 per day
        if user.subscription_tier == SubscriptionTier.BASIC:
            last_generation = await self._get_last_generation(user.id)
            
            if last_generation:
                time_since_last = current_time - last_generation
                if time_since_last < timedelta(days=1):
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "message": "Daily project generation limit reached",
                            "next_available": last_generation + timedelta(days=1),
                            "upgrade_url": "/Aoede/subscription/upgrade"
                        }
                    )
        
        # Track usage
        await self._track_usage(user.id, current_time)
        return True
    
    async def _track_usage(self, user_id: int, timestamp: datetime):
        """Track project generation usage"""
        usage_key = f"project_usage:{user_id}"
        usage_data = {
            "last_generated": timestamp.isoformat(),
            "count": 1
        }
        
        existing_data = self.redis_client.get(usage_key)
        if existing_data:
            data = json.loads(existing_data)
            data["count"] += 1
            usage_data = data
        
        self.redis_client.setex(
            usage_key,
            timedelta(days=30),  # Store usage data for 30 days
            json.dumps(usage_data)
        )
    
    async def _get_last_generation(self, user_id: int) -> Optional[datetime]:
        """Get user's last project generation timestamp"""
        usage_key = f"project_usage:{user_id}"
        usage_data = self.redis_client.get(usage_key)
        
        if usage_data:
            data = json.loads(usage_data)
            return datetime.fromisoformat(data["last_generated"])
        
        return None
