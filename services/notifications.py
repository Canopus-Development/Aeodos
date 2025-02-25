import logging
from typing import Dict, Any, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
from security import SecurityConfig

logger = logging.getLogger(__name__)

class NotificationManager:
    """Enterprise-grade real-time notification system"""
    
    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._admin_connections: Set[WebSocket] = set()
        self._internal_buffer: asyncio.Queue = asyncio.Queue()
        self._running = False
    
    async def connect(self, websocket: WebSocket, client_id: str, is_admin: bool = False):
        """Handle new WebSocket connections"""
        try:
            await websocket.accept()
            
            if is_admin:
                self._admin_connections.add(websocket)
                logger.info(f"Admin connected: {websocket.client.host}")
            else:
                if client_id not in self._connections:
                    self._connections[client_id] = set()
                self._connections[client_id].add(websocket)
                logger.info(f"Client connected: {client_id}")
            
            # Store connection info in Redis for tracking
            await self._track_connection(websocket, client_id, is_admin)
            
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            raise
    
    async def disconnect(self, websocket: WebSocket, client_id: str, is_admin: bool = False):
        """Handle WebSocket disconnections"""
        try:
            if is_admin and websocket in self._admin_connections:
                self._admin_connections.remove(websocket)
                logger.info(f"Admin disconnected: {websocket.client.host}")
            elif client_id in self._connections:
                self._connections[client_id].remove(websocket)
                if not self._connections[client_id]:
                    del self._connections[client_id]
                logger.info(f"Client disconnected: {client_id}")
            
            await self._track_disconnection(websocket, client_id, is_admin)
            
        except Exception as e:
            logger.error(f"Disconnection handling failed: {str(e)}")
    
    async def broadcast_to_user(self, client_id: str, message: Dict[str, Any]):
        """Send notification to specific user"""
        if client_id in self._connections:
            dead_connections = set()
            
            for websocket in self._connections[client_id]:
                try:
                    await websocket.send_json({
                        "type": "notification",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": message
                    })
                except WebSocketDisconnect:
                    dead_connections.add(websocket)
                except Exception as e:
                    logger.error(f"Failed to send to {client_id}: {str(e)}")
                    dead_connections.add(websocket)
            
            # Cleanup dead connections
            for dead in dead_connections:
                await self.disconnect(dead, client_id)
        
        # Store notification in Redis for offline users
        await self._store_offline_notification(client_id, message)
    
    async def broadcast_to_admins(self, message: Dict[str, Any]):
        """Send notification to admin dashboards"""
        dead_connections = set()
        
        for websocket in self._admin_connections:
            try:
                await websocket.send_json({
                    "type": "admin_notification",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": message
                })
            except WebSocketDisconnect:
                dead_connections.add(websocket)
            except Exception as e:
                logger.error(f"Failed to send to admin: {str(e)}")
                dead_connections.add(websocket)
        
        # Cleanup dead connections
        for dead in dead_connections:
            await self.disconnect(dead, "", True)
    
    async def _track_connection(self, websocket: WebSocket, client_id: str, is_admin: bool):
        """Track active connections in Redis"""
        connection_key = f"connections:{'admin' if is_admin else client_id}"
        SecurityConfig.redis_client.sadd(
            connection_key,
            f"{websocket.client.host}:{websocket.client.port}"
        )
    
    async def _track_disconnection(self, websocket: WebSocket, client_id: str, is_admin: bool):
        """Update connection tracking in Redis"""
        connection_key = f"connections:{'admin' if is_admin else client_id}"
        SecurityConfig.redis_client.srem(
            connection_key,
            f"{websocket.client.host}:{websocket.client.port}"
        )
    
    async def _store_offline_notification(self, client_id: str, message: Dict[str, Any]):
        """Store notifications for offline users"""
        notification_key = f"offline_notifications:{client_id}"
        SecurityConfig.redis_client.lpush(
            notification_key,
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "data": message
            })
        )
        SecurityConfig.redis_client.ltrim(notification_key, 0, 99)  # Keep last 100

    async def send_welcome_notification(self, user_id: str, company: str) -> None:
        """Send welcome notification to new user"""
        await self.broadcast_to_user(
            user_id,
            {
                "type": "welcome",
                "title": "Welcome to Aoede!",
                "message": f"Welcome {company} to Aoede! Your account has been successfully created.",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def notify_key_regeneration(self, user_id: str, reason: str = None) -> None:
        """Notify user about API key regeneration"""
        await self.broadcast_to_user(
            user_id,
            {
                "type": "security",
                "title": "API Key Regenerated",
                "message": "Your API key has been regenerated. Please update your applications.",
                "reason": reason or "Not specified",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Global notification manager instance
notification_manager = NotificationManager()

# Simplified public interface
async def send_welcome_notification(user_id: str, company: str) -> None:
    """Send welcome notification"""
    await notification_manager.send_welcome_notification(user_id, company)

async def notify_key_regeneration(user_id: str, reason: str = None) -> None:
    """Send key regeneration notification"""
    await notification_manager.notify_key_regeneration(user_id, reason)

async def send_subscription_notification(user_id: str, tier: str, status: str) -> None:
    """Send notification about subscription changes"""
    await notification_manager.broadcast_to_user(
        user_id,
        {
            "type": "subscription",
            "title": "Subscription Update",
            "message": f"Your subscription has been {status} to {tier} tier",
            "tier": tier,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Add to public interface
async def notify_subscription_change(user_id: str, tier: str, status: str) -> None:
    """Send subscription change notification"""
    await send_subscription_notification(user_id, tier, status)
