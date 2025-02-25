import os
import docker
import asyncio
import tempfile
from typing import Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SandboxManager:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.base_image = "Aoede/sandbox:latest"
        self.temp_dir = Path("/tmp/Aoede/sandbox")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_sandbox(self, project_id: str) -> str:
        """Create a new sandbox environment"""
        try:
            container = self.docker_client.containers.run(
                self.base_image,
                detach=True,
                remove=True,
                network_mode="none",  # Isolate network
                mem_limit="512m",     # Limit memory
                cpu_period=100000,    # CPU quota
                cpu_quota=50000,      # 50% CPU
                working_dir="/workspace",
                volumes={
                    str(self.temp_dir / project_id): {
                        'bind': '/workspace',
                        'mode': 'rw'
                    }
                }
            )
            return container.id
        except Exception as e:
            logger.error(f"Failed to create sandbox: {str(e)}")
            raise
    
    async def execute_code(
        self,
        container_id: str,
        code: Dict[str, str],
        test_command: str
    ) -> Dict[str, Any]:
        """Execute code in sandbox and return results"""
        try:
            container = self.docker_client.containers.get(container_id)
            
            # Write code files
            for filename, content in code.items():
                file_path = self.temp_dir / container_id / filename
                file_path.write_text(content)
            
            # Execute test command
            result = container.exec_run(
                test_command,
                workdir="/workspace",
                environment={
                    "PYTHONPATH": "/workspace",
                    "NODE_PATH": "/workspace/node_modules"
                }
            )
            
            return {
                "exit_code": result.exit_code,
                "output": result.output.decode(),
                "error": None if result.exit_code == 0 else "Test failed"
            }
        except Exception as e:
            logger.error(f"Code execution failed: {str(e)}")
            return {
                "exit_code": 1,
                "output": "",
                "error": str(e)
            }
    
    async def cleanup(self, container_id: str):
        """Cleanup sandbox environment"""
        try:
            container = self.docker_client.containers.get(container_id)
            container.stop()
            # Cleanup temp files
            (self.temp_dir / container_id).rmdir()
        except Exception as e:
            logger.error(f"Sandbox cleanup failed: {str(e)}")
