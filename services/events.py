from typing import Dict, Any, List
import logging
from datetime import datetime
import json
import aiohttp
import asyncio
import secrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from security import SecurityConfig
from database import SQLALCHEMY_DATABASE_URL, SubscriptionTier
from models.user import User

logger = logging.getLogger(__name__)

# Create a separate database session for event handling
engine = create_engine(SQLALCHEMY_DATABASE_URL)
EventSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DiscordNotifier:
    """Enterprise-grade Discord notification system"""
    WEBHOOK_URL = "https://discord.com/api/webhooks/1328336082710036490/2LMjHsFZVZyS3UpHaeGuqnetkhxLov8SVJb58HNzP_APPfT4cPC9cGnfyuw7_G_D4vuo"
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    @classmethod
    async def send_notification(cls, event_type: str, event_data: Dict[str, Any]) -> None:
        """Send notification to Discord with retries"""
        embed = cls._create_embed(event_type, event_data)
        
        for attempt in range(cls.MAX_RETRIES):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        cls.WEBHOOK_URL,
                        json={"embeds": [embed]},
                        timeout=10
                    ) as response:
                        if response.status == 204:
                            logger.info(f"Discord notification sent for event: {event_type}")
                            return
                        else:
                            logger.warning(
                                f"Discord API responded with status {response.status}: "
                                f"{await response.text()}"
                            )
            except Exception as e:
                logger.error(f"Discord notification attempt {attempt + 1} failed: {str(e)}")
                if attempt < cls.MAX_RETRIES - 1:
                    await asyncio.sleep(cls.RETRY_DELAY * (attempt + 1))
                else:
                    logger.error("Max retries reached for Discord notification")
                    raise
    
    @classmethod
    def _create_embed(cls, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Discord embed for event"""
        color_map = {
            "user_created": 0x00ff00,  # Green
            "api_key_regenerated": 0xffff00,  # Yellow
            "project_generated": 0x0000ff,  # Blue
            "error_occurred": 0xff0000,  # Red
        }
        
        return {
            "title": f"Aoede Event: {event_type}",
            "color": color_map.get(event_type, 0x808080),
            "description": cls._format_description(event_data),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Aoede AI Platform"
            },
            "fields": cls._create_fields(event_data)
        }
    
    @classmethod
    def _format_description(cls, event_data: Dict[str, Any]) -> str:
        """Format event description"""
        return f"Event details for ID: {event_data.get('user_id', 'N/A')}"
    
    @classmethod
    def _create_fields(cls, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create fields for Discord embed"""
        fields = []
        for key, value in event_data.items():
            if key != "user_id":
                fields.append({
                    "name": key.replace("_", " ").title(),
                    "value": str(value),
                    "inline": True
                })
        return fields

class EventMetrics:
    """Enterprise-grade metrics tracking"""
    
    @classmethod
    async def track_event(cls, event_type: str, data: Dict[str, Any]) -> None:
        """Track event metrics in Redis"""
        try:
            key_prefix = f"metrics:{event_type}:"
            current_hour = datetime.utcnow().strftime("%Y%m%d%H")
            
            pipeline = SecurityConfig.redis_client.pipeline()
            
            # Increment total count
            pipeline.incr(f"{key_prefix}total")
            
            # Increment hourly count
            pipeline.incr(f"{key_prefix}hourly:{current_hour}")
            pipeline.expire(f"{key_prefix}hourly:{current_hour}", 86400)  # 24h retention
            
            # Track unique users
            if data.get('user_id'):
                pipeline.sadd(f"{key_prefix}users:{current_hour}", data['user_id'])
                pipeline.expire(f"{key_prefix}users:{current_hour}", 86400)
            
            pipeline.execute()
            
        except Exception as e:
            logger.error(f"Failed to track event metrics: {str(e)}")

class EventHandler:
    """Enterprise-grade event handling system"""
    
    EVENT_TYPES = {
        "user_created": "user.created",
        "api_key_regenerated": "api.key.regenerated",
        "project_generated": "project.generated",
        "error_occurred": "system.error",
        "subscription_updated": "subscription.updated",
        "system_alert": "system.alert"
    }
    
    @classmethod
    async def handle_event(cls, event_type: str, data: Dict[str, Any]) -> None:
        """Handle system events"""
        if event_type not in cls.EVENT_TYPES:
            logger.error(f"Invalid event type: {event_type}")
            return
            
        event_data = {
            "type": cls.EVENT_TYPES[event_type],
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        try:
            # Store event in Redis
            event_key = f"events:{event_type}:{datetime.utcnow().timestamp()}"
            SecurityConfig.redis_client.setex(
                event_key,
                86400,  # 24 hours retention
                json.dumps(event_data)
            )
            
            # Send Discord notification
            await DiscordNotifier.send_notification(event_type, data)
            
            # Process event
            await cls._process_event(event_type, event_data)
            
        except Exception as e:
            logger.error(f"Event handling failed: {str(e)}")
            # Send error notification
            await cls._handle_error({
                "error": str(e),
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat()
            })
            raise
    
    @classmethod
    async def _process_event(cls, event_type: str, event_data: Dict[str, Any]) -> None:
        """Process different types of events"""
        processors = {
            "user_created": cls._handle_user_created,
            "api_key_regenerated": cls._handle_key_regenerated,
            "project_generated": cls._handle_project_generated,
            "error_occurred": cls._handle_error
        }
        
        processor = processors.get(event_type)
        if processor:
            await processor(event_data)
    
    @classmethod
    async def _handle_user_created(cls, event_data: Dict[str, Any]) -> None:
        """Handle user creation events"""
        try:
            user_id = event_data['data'].get('user_id')
            if not user_id:
                raise ValueError("User ID is required")
            
            # Track user creation metrics
            await EventMetrics.track_event('user_created', event_data['data'])
            
            # Store user analytics data
            analytics_key = f"user_analytics:{user_id}"
            SecurityConfig.redis_client.hset(
                analytics_key,
                mapping={
                    'created_at': event_data['timestamp'],
                    'source': event_data['data'].get('source', 'api'),
                    'company': event_data['data'].get('company', 'unknown')
                }
            )
            
            # Send welcome notification
            await DiscordNotifier.send_notification(
                'user_created',
                {
                    'user_id': user_id,
                    'company': event_data['data'].get('company'),
                    'message': "New user registration"
                }
            )
            
        except Exception as e:
            logger.error(f"User creation event handling failed: {str(e)}")
            await cls._handle_error({'error': str(e), 'context': event_data})
    
    @classmethod
    async def _handle_key_regenerated(cls, event_data: Dict[str, Any]) -> None:
        """Handle API key regeneration events"""
        try:
            user_id = event_data['data'].get('user_id')
            if not user_id:
                raise ValueError("User ID is required")
            
            # Track key regeneration
            await EventMetrics.track_event('api_key_regenerated', event_data['data'])
            
            # Update security logs
            security_log = {
                'event': 'key_regeneration',
                'user_id': user_id,
                'timestamp': event_data['timestamp'],
                'reason': event_data['data'].get('reason', 'not specified')
            }
            
            SecurityConfig.redis_client.lpush(
                f"security_logs:user:{user_id}",
                json.dumps(security_log)
            )
            
            # Send security notification
            await DiscordNotifier.send_notification(
                'api_key_regenerated',
                {
                    'user_id': user_id,
                    'reason': event_data['data'].get('reason'),
                    'message': "API Key regenerated"
                }
            )
            
        except Exception as e:
            logger.error(f"Key regeneration event handling failed: {str(e)}")
            await cls._handle_error({'error': str(e), 'context': event_data})
    
    @classmethod
    async def _handle_project_generated(cls, event_data: Dict[str, Any]) -> None:
        """Handle project generation events"""
        try:
            project_id = event_data['data'].get('project_id')
            user_id = event_data['data'].get('user_id')
            
            if not all([project_id, user_id]):
                raise ValueError("Project ID and User ID are required")
            
            # Track project metrics
            await EventMetrics.track_event('project_generated', event_data['data'])
            
            # Update user's project count
            with EventSession() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.projects_generated_count += 1
                    session.commit()
            
            # Store project analytics
            analytics_key = f"project_analytics:{project_id}"
            SecurityConfig.redis_client.hset(
                analytics_key,
                mapping={
                    'generated_at': event_data['timestamp'],
                    'user_id': user_id,
                    'type': event_data['data'].get('type', 'standard'),
                    'status': 'completed'
                }
            )
            
            # Send project completion notification
            await DiscordNotifier.send_notification(
                'project_generated',
                {
                    'project_id': project_id,
                    'user_id': user_id,
                    'message': "Project generation completed"
                }
            )
            
        except Exception as e:
            logger.error(f"Project generation event handling failed: {str(e)}")
            await cls._handle_error({'error': str(e), 'context': event_data})
    
    @classmethod
    async def _handle_error(cls, event_data: Dict[str, Any]) -> None:
        """Handle error events"""
        try:
            error_id = f"error_{secrets.token_hex(8)}"
            
            # Track error metrics
            await EventMetrics.track_event('error_occurred', event_data)
            
            # Store error details
            error_key = f"errors:{error_id}"
            SecurityConfig.redis_client.hset(
                error_key,
                mapping={
                    'timestamp': datetime.utcnow().isoformat(),
                    'error': event_data.get('error', 'Unknown error'),
                    'context': json.dumps(event_data.get('context', {}))
                }
            )
            SecurityConfig.redis_client.expire(error_key, 604800)  # 7 days retention
            
            # Send error notification
            await DiscordNotifier.send_notification(
                'error_occurred',
                {
                    'error_id': error_id,
                    'error': event_data.get('error'),
                    'message': "System error occurred"
                }
            )
            
        except Exception as e:
            logger.error(f"Error event handling failed: {str(e)}")
