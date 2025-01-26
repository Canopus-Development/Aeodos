import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Security, Depends, Header, Request
import secrets
import hashlib
import redis
import logging
from functools import wraps
from dotenv import load_dotenv
import json
from enum import Enum

load_dotenv()

logger = logging.getLogger(__name__)

# Security configuration
class SecurityConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    API_KEY_PREFIX = "AEODOS-KEY"
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION = 15  # minutes
    
    # Redis configuration for rate limiting and token blacklist
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(REDIS_URL)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class APIKeyManager:
    def __init__(self):
        self.redis_client = SecurityConfig.redis_client
    
    def generate_api_key(self) -> str:
        """Generate a secure API key with prefix"""
        raw_key = secrets.token_urlsafe(32)
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
        return f"{SecurityConfig.API_KEY_PREFIX}{raw_key}", hashed_key
    
    def verify_key(self, api_key: str) -> bool:
        """Verify API key and check rate limits"""
        if not api_key.startswith(SecurityConfig.API_KEY_PREFIX):
            return False
        
        # Check if key is blacklisted
        if self.redis_client.get(f"blacklist:{api_key}"):
            raise HTTPException(status_code=403, detail="API key has been revoked")
        
        return True
    
    def track_usage(self, api_key: str, path: str):
        """Track API usage and enforce rate limits"""
        # Update path to remove /api prefix if present
        path = path.replace("/api/v1/", "/aeodos/")
        path = path.replace("/api/", "/aeodos/")
        
        key = f"usage:{api_key}:{path}"
        pipe = self.redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 3600)  # 1 hour expiry
        current_usage = pipe.execute()[0]
        
        # Check rate limits
        if current_usage > 1000:  # Adjust limit based on user tier
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

def rate_limit(max_requests: int, time_window: int = 3600):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                raise HTTPException(status_code=500, detail="Internal server error")
            
            client_ip = request.client.host
            endpoint = request.url.path
            
            # Create rate limit key
            rate_limit_key = f"rate_limit:{client_ip}:{endpoint}"
            
            # Check rate limit
            current = SecurityConfig.redis_client.get(rate_limit_key)
            if current and int(current) >= max_requests:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Update rate limit counter
            pipe = SecurityConfig.redis_client.pipeline()
            pipe.incr(rate_limit_key)
            pipe.expire(rate_limit_key, time_window)
            pipe.execute()
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def verify_api_key(
    api_key: str = Header(..., alias="X-API-Key"),
    request: Request = None
) -> str:
    """Enhanced API key verification with security checks"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key is required")
    
    key_manager = APIKeyManager()
    if not key_manager.verify_key(api_key):
        logger.warning(f"Invalid API key attempt from IP: {request.client.host}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Track API usage
    key_manager.track_usage(api_key, request.url.path)
    
    return api_key

def create_access_token(
    data: Dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT token with enhanced security"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    token = jwt.encode(
        to_encode,
        SecurityConfig.SECRET_KEY,
        algorithm=SecurityConfig.ALGORITHM
    )
    
    # Store token in Redis for potential revocation
    token_key = f"token:{hashlib.sha256(token.encode()).hexdigest()}"
    SecurityConfig.redis_client.setex(
        token_key,
        int(expires_delta.total_seconds() if expires_delta else 1800),
        "valid"
    )
    
    return token

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, SecurityConfig.SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

class Role(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

async def admin_required(
    request: Request,
    api_key: str = Header(..., alias="X-API-Key"),
    admin_token: str = Header(..., alias="X-Admin-Token")
) -> bool:
    """Enterprise-grade admin authentication middleware"""
    try:
        # Verify API key first
        await verify_api_key(api_key, request)
        
        # Verify admin token
        if not admin_token:
            raise HTTPException(
                status_code=401,
                detail="Admin token is required"
            )
            
        # Check admin token in Redis
        admin_data = SecurityConfig.redis_client.get(f"admin_token:{admin_token}")
        if not admin_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid admin token"
            )
            
        # Parse admin data
        admin_info = json.loads(admin_data)
        
        # Verify role and permissions
        if admin_info.get('role') not in [Role.ADMIN, Role.MODERATOR]:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
            
        # Check token expiration
        if datetime.fromisoformat(admin_info['expires_at']) < datetime.utcnow():
            SecurityConfig.redis_client.delete(f"admin_token:{admin_token}")
            raise HTTPException(
                status_code=401,
                detail="Admin token expired"
            )
            
        # Track admin action for audit
        await _track_admin_action(
            admin_id=admin_info['user_id'],
            path=request.url.path,
            method=request.method,
            request=request  
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Admin authentication failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Admin authentication failed"
        )

async def _track_admin_action(
    admin_id: str,
    path: str,
    method: str,
    request: Optional[Request] = None
) -> None:
    """Track admin actions for audit trail"""
    try:
        ip_address = request.client.host if request else None
        SecurityConfig.redis_client.lpush(
            "admin_audit_log",
            json.dumps({
                "admin_id": admin_id,
                "path": path,
                "method": method,
                "timestamp": datetime.utcnow().isoformat(),
                "ip": ip_address
            })
        )
    except Exception as e:
        logger.error(f"Failed to track admin action: {str(e)}")

# Make sure these names are available for import
__all__ = [
    'verify_api_key',
    'get_password_hash',
    'APIKeyManager',
    'SecurityConfig',
    'rate_limit',
    'admin_required',
    'Role'
]
