from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from services.notifications import notification_manager
from security import verify_api_key, SecurityConfig
from database import get_db
from models.user import User
import logging
import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

class WebSocketManager:
    """Enterprise-grade WebSocket connection manager"""
    HEARTBEAT_INTERVAL = 30  # seconds
    
    @staticmethod
    async def verify_admin(api_key: str, db) -> bool:
        """Verify admin privileges"""
        try:
            user = db.query(User).filter(User.api_key == api_key).first()
            return user and user.subscription_tier == "enterprise"
        except Exception as e:
            logger.error(f"Admin verification failed: {str(e)}")
            return False
    
    @staticmethod
    async def process_message(message: str, websocket: WebSocket, is_admin: bool) -> None:
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "heartbeat":
                await websocket.send_json({"type": "heartbeat_ack"})
            elif message_type == "command" and is_admin:
                await WebSocketManager._handle_admin_command(data, websocket)
            else:
                await WebSocketManager._handle_client_message(data, websocket)
                
        except json.JSONDecodeError:
            logger.warning(f"Invalid message format from {websocket.client.host}")
        except Exception as e:
            logger.error(f"Message processing failed: {str(e)}")
    
    @staticmethod
    async def _handle_admin_command(data: Dict[str, Any], websocket: WebSocket) -> None:
        """Handle admin commands"""
        command = data.get("command")
        if command == "broadcast":
            await notification_manager.broadcast_to_admins({
                "type": "broadcast",
                "message": data.get("message"),
                "sender": websocket.client.host
            })
        elif command == "system_status":
            status = await WebSocketManager._get_system_status()
            await websocket.send_json(status)
    
    @staticmethod
    async def _handle_client_message(data: Dict[str, Any], websocket: WebSocket) -> None:
        """Handle regular client messages"""
        # Implement client message handling logic
        pass
    
    @staticmethod
    async def _get_system_status() -> Dict[str, Any]:
        """Get system status for admin dashboard"""
        return {
            "type": "system_status",
            "timestamp": datetime.utcnow().isoformat(),
            "connections": {
                "total": len(notification_manager._connections),
                "admin": len(notification_manager._admin_connections)
            },
            "memory_usage": await WebSocketManager._get_memory_usage()
        }
    
    @staticmethod
    async def _get_memory_usage() -> Dict[str, float]:
        """Get memory usage statistics"""
        import psutil
        process = psutil.Process()
        return {
            "percent": process.memory_percent(),
            "rss": process.memory_info().rss / 1024 / 1024  # MB
        }
    
    @staticmethod
    async def start_heartbeat(websocket: WebSocket) -> None:
        """Start heartbeat for connection monitoring"""
        while True:
            try:
                await asyncio.sleep(WebSocketManager.HEARTBEAT_INTERVAL)
                await websocket.send_json({"type": "heartbeat"})
            except Exception:
                break

@router.websocket("/Aoede/ws/notifications")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    api_key: str,
    db = Depends(get_db)
):
    """WebSocket endpoint for user notifications"""
    try:
        # Verify API key
        await verify_api_key(api_key)
        
        # Connect to notification system
        await notification_manager.connect(websocket, client_id)
        
        # Start heartbeat in background
        heartbeat_task = asyncio.create_task(
            WebSocketManager.start_heartbeat(websocket)
        )
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                await WebSocketManager.process_message(data, websocket, False)
                
        except WebSocketDisconnect:
            await notification_manager.disconnect(websocket, client_id)
        finally:
            heartbeat_task.cancel()
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1008)  # Policy violation

@router.websocket("/Aoede/ws/admin")
async def admin_websocket_endpoint(
    websocket: WebSocket,
    api_key: str,
    db = Depends(get_db)
):
    """WebSocket endpoint for admin notifications"""
    try:
        # Verify admin API key
        is_admin = await WebSocketManager.verify_admin(api_key, db)
        if not is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Connect to notification system
        await notification_manager.connect(websocket, "", True)
        
        # Start heartbeat in background
        heartbeat_task = asyncio.create_task(
            WebSocketManager.start_heartbeat(websocket)
        )
        
        # Send initial system status
        await websocket.send_json(
            await WebSocketManager._get_system_status()
        )
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                await WebSocketManager.process_message(data, websocket, True)
                
        except WebSocketDisconnect:
            await notification_manager.disconnect(websocket, "", True)
        finally:
            heartbeat_task.cancel()
            
    except Exception as e:
        logger.error(f"Admin WebSocket error: {str(e)}")
        await websocket.close(code=1008)
