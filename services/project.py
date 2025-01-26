from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
import logging
from datetime import datetime
import json

from services.ai import WebsiteGenerationService, DocumentationService, DebugService
from services.sandbox import SandboxManager
from database import SubscriptionTier

logger = logging.getLogger(__name__)

class ProjectStatus(str, Enum):
    INITIALIZING = "initializing"
    GENERATING = "generating"
    VALIDATING = "validating"
    FIXING = "fixing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProjectGenerator:
    def __init__(self, redis_client, user_tier: SubscriptionTier):
        self.redis_client = redis_client
        self.user_tier = user_tier
        self.website_service = WebsiteGenerationService()
        self.debug_service = DebugService()
        self.sandbox_manager = SandboxManager()
        self.max_iterations = 5
        self.status_key_prefix = "project_status:"
    
    async def generate_project(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main project generation orchestrator with sandbox validation"""
        sandbox_id = None
        try:
            await self._update_status(project_id, ProjectStatus.INITIALIZING)
            
            # Create sandbox environment
            sandbox_id = await self.sandbox_manager.create_sandbox(project_id)
            
            # Initialize project
            project = await self._initialize_project(data)
            
            # Generate and validate code loop
            await self._update_status(project_id, ProjectStatus.GENERATING)
            code = await self._generate_code(project)
            
            iteration = 0
            while iteration < self.max_iterations:
                await self._update_status(project_id, ProjectStatus.VALIDATING)
                validation = await self._validate_code(code, sandbox_id)
                
                if validation["is_valid"]:
                    break
                
                await self._update_status(project_id, ProjectStatus.FIXING)
                code = await self._fix_code(code, validation["errors"], sandbox_id)
                iteration += 1
            
            if iteration == self.max_iterations:
                raise Exception("Could not fix all issues within iteration limit")
            
            # Finalize project
            result = await self._finalize_project(project_id, code, sandbox_id)
            await self._update_status(project_id, ProjectStatus.COMPLETED)
            
            return result
            
        except Exception as e:
            await self._update_status(project_id, ProjectStatus.FAILED, error=str(e))
            raise
        finally:
            if sandbox_id:
                await self.sandbox_manager.cleanup(sandbox_id)
    
    async def _initialize_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize project structure based on requirements"""
        return {
            "structure": await self._generate_project_structure(data),
            "requirements": await self._analyze_requirements(data),
            "config": await self._generate_config(data)
        }
    
    async def _generate_code(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Generate initial codebase"""
        tasks = [
            self._generate_frontend(project),
            self._generate_backend(project),
            self._generate_database(project),
            self._generate_api(project)
        ]
        results = await asyncio.gather(*tasks)
        return {
            "frontend": results[0],
            "backend": results[1],
            "database": results[2],
            "api": results[3]
        }
    
    async def _validate_code(self, code: Dict[str, Any], sandbox_id: str) -> Dict[str, Any]:
        """Validate generated code using sandbox environment"""
        validation_tasks = [
            self._validate_frontend(code["frontend"], sandbox_id),
            self._validate_backend(code["backend"], sandbox_id),
            self._validate_integration(code, sandbox_id)
        ]
        
        results = await asyncio.gather(*validation_tasks)
        return self._process_validation_results(results)
    
    async def _validate_frontend(self, code: Dict[str, str], sandbox_id: str) -> Dict[str, Any]:
        """Validate frontend code in sandbox"""
        # Write frontend files
        frontend_code = {
            "index.html": code["html"],
            "styles.css": code["css"],
            "app.js": code["js"]
        }
        
        # Run frontend tests
        result = await self.sandbox_manager.execute_code(
            sandbox_id,
            frontend_code,
            "npm test && npx eslint . && npx stylelint '**/*.css'"
        )
        
        return {
            "is_valid": result["exit_code"] == 0,
            "errors": self._parse_frontend_errors(result["output"]) if result["exit_code"] != 0 else []
        }
    
    async def _validate_backend(self, code: Dict[str, str], sandbox_id: str) -> Dict[str, Any]:
        """Validate backend code in sandbox"""
        backend_code = {
            "main.py": code["main"],
            "test_main.py": code["tests"]
        }
        
        result = await self.sandbox_manager.execute_code(
            sandbox_id,
            backend_code,
            "pytest && pylint **/*.py"
        )
        
        return {
            "is_valid": result["exit_code"] == 0,
            "errors": self._parse_backend_errors(result["output"]) if result["exit_code"] != 0 else []
        }
    
    async def _fix_code(self, code: Dict[str, Any], errors: List[Dict], sandbox_id: str) -> Dict[str, Any]:
        """Fix code issues using AI and validate in sandbox"""
        try:
            # Get AI fixes
            fixes = await self._get_ai_fixes(code, errors)
            
            # Apply fixes
            fixed_code = await self._apply_fixes(code, fixes)
            
            # Validate fixes in sandbox
            validation = await self._validate_code(fixed_code, sandbox_id)
            
            if not validation["is_valid"]:
                logger.warning("Fixes did not resolve all issues")
            
            return fixed_code
            
        except Exception as e:
            logger.error(f"Code fixing failed: {str(e)}")
            raise
    
    async def _update_status(
        self,
        project_id: str,
        status: ProjectStatus,
        error: Optional[str] = None
    ):
        """Update project generation status"""
        status_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
            "error": error
        }
        await self.redis_client.set(
            f"{self.status_key_prefix}{project_id}",
            json.dumps(status_data)
        )
