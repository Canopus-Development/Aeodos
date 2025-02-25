from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request, Header, BackgroundTasks, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import asyncio
import logging
import time
from datetime import datetime
import json
import secrets
from models.user import User
from database import get_db
from security import verify_api_key, get_password_hash, APIKeyManager, SecurityConfig, rate_limit
from services.ai import WebsiteGenerationService, DocumentationService, DebugService
from utils.rate_limiters import ProjectGenerationLimiter
from routers import subscription, admin
from services.project import ProjectGenerator, ProjectStatus
from utils.validators import validate_project_request, validate_version_compatibility
from utils.health import check_database_health, check_redis_health, check_ai_models_health
from utils.metrics import track_project_generation, track_generation_metrics, UsageTracker
from services.generator import get_generation_service
from services.events import EventHandler
from routers import websocket

# Enhanced logging configuration
logging.basicConfig(
    filename='api.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enterprise-grade lifespan management"""
    try:
        # Startup
        asyncio.create_task(async_handler.process_queue())
        logger.info("Aoede API started successfully")
        yield
        # Shutdown
        logger.info("Shutting down Aoede API")
    except Exception as e:
        logger.error(f"Lifespan error: {str(e)}")
        raise

# Initialize FastAPI with enhanced configuration
app = FastAPI(
    title="Aoede API",
    description="Enterprise-Grade AI-Powered No-Code Website Builder API",
    version="0.1.0",
    docs_url="/Aoede/docs",
    redoc_url="/Aoede/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "websites", "description": "Website generation operations"},
        {"name": "auth", "description": "Authentication operations"},
        {"name": "monitoring", "description": "System monitoring endpoints"},
        {"name": "generation", "description": "Code generation operations"}
    ],
    openapi_url="/Aoede/openapi.json",
    servers=[
        {"url": "https://api.canopus.software", "description": "Production server"},
        {"url": "http://localhost:8000", "description": "Development server"}
    ]
)
limiter = Limiter(key_func=get_remote_address)

# Add rate limiting
app.state.limiter = limiter

# Add enterprise-grade middleware
app.add_middleware(HTTPSRedirectMiddleware)  # Force HTTPS
# Security middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "api.canopus.software",
        "localhost",
        "127.0.0.1"
    ]
)

class APIKeyRequest(BaseModel):
    email: EmailStr
    company_name: str

class APIKeyRegenRequest(BaseModel):
    current_api_key: str
    reason: Optional[str] = None

class WebsiteRequest(BaseModel):
    description: str
    style: Optional[str] = "modern"
    pages: Optional[list] = ["home"]

class AoedeWebsite(BaseModel):
    name: str
    description: str
    style: Optional[str] = "modern"
    pages: Optional[list] = ["home"]
    business_type: Optional[str] = "general"
    color_scheme: Optional[str] = "default"

class GenerateRequest(BaseModel):
    project_name: str
    description: str
    version: str = "1.0"
    components: List[str] = []
    settings: Dict[str, Any] = {}

class ProjectRequest(GenerateRequest):
    frontend_config: Dict[str, Any]
    backend_config: Dict[str, Any]
    deployment_config: Optional[Dict[str, Any]] = None

class RequestValidator:
    """Validate and sanitize incoming requests"""
    @staticmethod
    def validate_website_data(website: AoedeWebsite) -> None:
        if len(website.name) < 3:
            raise HTTPException(
                status_code=422,
                detail="Website name must be at least 3 characters long"
            )
class AsyncRequestHandler:
    """Handle async request processing"""
    def __init__(self):
        self.queue = asyncio.Queue()
        self.processing = False
    
    async def process_queue(self):
        while True:
            if not self.queue.empty():
                task = await self.queue.get()
                await self.execute_task(task)
            await asyncio.sleep(0.1)
    
    async def execute_task(self, task: Dict):
        try:
            # Process the task
            result = await task['service'].generate_website(task['data'])
            # Store result in cache/database
            await self.store_result(task['id'], result)
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            await self.handle_task_error(task['id'], str(e))

# Initialize async handler
async_handler = AsyncRequestHandler()

# API Key Management Routes
@app.post("/Aoede/keys/generate", tags=["auth"])
async def generate_new_api_key(
    request: APIKeyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate new API key with enhanced security and tracking"""
    try:
        api_key_manager = APIKeyManager()
        api_key, hashed_key = api_key_manager.generate_api_key()
        
        new_user = User(
            email=request.email,
            api_key=hashed_key,
            username=request.company_name,
            tier="free",
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        
        # Replace email with event handling
        background_tasks.add_task(
            EventHandler.handle_event,
            "user_created",
            {
                "user_id": new_user.id,
                "email": request.email,
                "company": request.company_name
            }
        )
        
        return {
            "api_key": api_key,
            "expires_in": "30 days",
            "rate_limit": "100 requests/hour"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"API key generation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/Aoede/keys/regenerate", tags=["auth"])
async def regenerate_api_key(
    request: APIKeyRegenRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Regenerate API key with security measures"""
    try:
        user = db.query(User).filter(
            User.api_key == request.current_api_key
        ).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Generate new key
        api_key_manager = APIKeyManager()
        new_api_key, new_hashed_key = api_key_manager.generate_api_key()
        
        # Update user record
        user.api_key = new_hashed_key
        user.key_regenerated_at = datetime.utcnow()
        db.commit()
        
        # Replace email with event handling
        background_tasks.add_task(
            EventHandler.handle_event,
            "api_key_regenerated",
            {
                "user_id": user.id,
                "reason": request.reason
            }
        )
        
        return {"new_api_key": new_api_key}
    except Exception as e:
        db.rollback()
        logger.error(f"API key regeneration failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/Aoede/usage", tags=["monitoring"])
async def get_api_usage(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Get detailed API usage metrics"""
    try:
        usage_data = await UsageTracker.get_detailed_metrics(api_key)
        return {
            "current_period": {
                "start": usage_data["period_start"],
                "end": usage_data["period_end"],
                "requests": usage_data["total_requests"],
                "quota": usage_data["quota"],
            },
            "rate_limits": {
                "hour": usage_data["hourly_usage"],
                "day": usage_data["daily_usage"],
                "month": usage_data["monthly_usage"]
            },
            "endpoints": usage_data["endpoint_usage"]
        }
    except Exception as e:
        logger.error(f"Usage retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Generation Routes
@app.post("/Aoede/generate/frontend", tags=["generation"])
@rate_limit(max_requests=20, time_window=3600)
async def generate_frontend(
    request: Request,
    data: GenerateRequest,
    version: str = Path(..., pattern="^v[1-9]$"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Generate frontend code with version control"""
    return await handle_generation_request(
        request, version, data, api_key, "frontend"
    )

@app.post("/Aoede/generate/backend", tags=["generation"])
@rate_limit(max_requests=20, time_window=3600)
async def generate_backend(
    request: Request,
    data: GenerateRequest,
    version: str = Path(..., pattern="^v[1-9]$"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Generate backend code with version control"""
    return await handle_generation_request(
        request, version, data, api_key, "backend"
    )

@app.post("/Aoede/generate/debug", tags=["generation"])
@rate_limit(max_requests=50, time_window=3600)
async def generate_debug(
    request: Request,
    data: GenerateRequest,
    version: str = Path(..., pattern="^v[1-9]$"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Generate debug analysis with version control"""
    return await handle_generation_request(
        request, version, data, api_key, "debug"
    )

@app.post("/Aoede/generate/project", tags=["generation"])
@rate_limit(max_requests=10, time_window=3600)  # Global rate limit
async def generate_project(
    request: Request,
    data: ProjectRequest,
    version: str = Path(..., pattern="^v[1-9]$"),
    background_tasks: BackgroundTasks = None,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Generate complete project with AI agent and error correction"""
    try:
        # Verify user and check limits
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        await validate_project_request(data)
        
        # Create project ID and initialize generator
        project_id = f"proj_{secrets.token_urlsafe(8)}"
        generator = ProjectGenerator(
            redis_client=SecurityConfig.redis_client,
            user_tier=user.subscription_tier
        )
        
        # Start async generation
        background_tasks.add_task(
            generator.generate_project,
            project_id=project_id,
            data=data.dict()
        )
        
        # Track metrics
        background_tasks.add_task(
            track_project_generation,
            user_id=user.id,
            project_id=project_id,
            tier=user.subscription_tier
        )
        
        return {
            "message": "Project generation started",
            "project_id": project_id,
            "status_check_url": f"/Aoede/projects/{project_id}/status",
            "estimated_time": "5-10 minutes",
            "tier": user.subscription_tier
        }
        
    except Exception as e:
        logger.error(f"Project generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Project generation failed",
                "error": str(e)
            }
        )

@app.get("/Aoede/projects/{project_id}/status", tags=["generation"])
async def get_project_status(
    project_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get project generation status"""
    try:
        status_data = await SecurityConfig.redis_client.get(
            f"project_status:{project_id}"
        )
        
        if not status_data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        status = json.loads(status_data)
        return {
            "project_id": project_id,
            "status": status["status"],
            "updated_at": status["updated_at"],
            "error": status.get("error")
        }
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def start_project_generation(
    user: User,
    data: ProjectRequest,
    background_tasks: BackgroundTasks,
    db: Session
) -> str:
    """Handle project generation process"""
    project_id = f"proj_{secrets.token_urlsafe(8)}"
    
    # Update user's project generation count
    user.projects_generated_count += 1
    user.last_project_generated = datetime.utcnow()
    db.commit()
    
    # Add generation task to queue
    await async_handler.queue.put({
        'id': project_id,
        'user_id': user.id,
        'type': 'project',
        'data': data.dict(),
        'tier': user.subscription_tier
    })
    
    # Track metrics
    background_tasks.add_task(
        track_project_generation,
        user_id=user.id,
        project_id=project_id,
        tier=user.subscription_tier
    )
    
    return project_id

async def handle_generation_request(
    request: Request,
    version: str,
    data: GenerateRequest,
    api_key: str,
    generation_type: str
) -> Dict[str, Any]:
    """Handle all generation requests with proper error handling and logging"""
    start_time = time.time()
    
    try:
        # Validate version compatibility
        await validate_version_compatibility(version, generation_type)
        
        # Get appropriate service
        service = get_generation_service(generation_type)
        
        # Generate content
        result = await service.generate(data.dict())
        
        # Track metrics
        await track_generation_metrics(
            api_key=api_key,
            generation_type=generation_type,
            duration=time.time() - start_time
        )
        
        return {
            "success": True,
            "version": version,
            "generation_type": generation_type,
            "content": result
        }
        
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"{generation_type} generation failed",
                "error": str(e)
            }
        )

# Enhanced health check endpoint
@app.get("/Aoede/health", tags=["monitoring"])
async def health_check():
    """Enhanced health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": app.version,
        "services": {
            "database": check_database_health(),
            "redis": check_redis_health(),
            "ai_models": check_ai_models_health()
        }
    }

# Include routers
app.include_router(subscription.router)
app.include_router(admin.router)
app.include_router(websocket.router)

if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Configure logging for production
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
                "level": "INFO"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "api.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "default",
                "level": "INFO"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    })

    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7297"))
    workers = int(os.getenv("WORKERS", "4"))
    reload = os.getenv("ENV", "production").lower() == "development"

    # Start server with enterprise-grade configuration
    try:
        logger.info(f"Starting Aoede API on {host}:{port}")
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            workers=workers,
            reload=reload,
            log_level="info",
            access_log=True,
            proxy_headers=True,
            forwarded_allow_ips="*",
            log_config=None  # Use our custom logging config
        )
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}")
        sys.exit(1)
