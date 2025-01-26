import os
import json
import logging
from typing import Dict, Any, List, Optional
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    SystemMessage, UserMessage, AssistantMessage, ToolMessage,
    CompletionsFinishReason, ChatCompletionsToolCall
)
from azure.core.credentials import AzureKeyCredential
from functools import lru_cache
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from .tools import (
    frontend_generator, 
    backend_generator, 
    debug_analyzer,
    internet_search, 
    rag_query,
    search_internet,
    query_knowledge_base
)

load_dotenv()

logger = logging.getLogger(__name__)

class AIConfig:  # Changed from AIModelConfig
    """Configuration for AI models"""
    ENDPOINT = "https://models.inference.ai.azure.com"
    TOKEN = os.getenv("AZURE_TOKEN")
    
    MODELS = {
        "frontend": "gpt-4o",
        "backend": "Codestral-2501",
        "debug": "Cohere-command-r-plus",
        "docs": "Llama-3.3-70B-Instruct"
    }
    
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    CACHE_TTL = 3600  # 1 hour

class BaseAIService:
    """Base class for AI services"""
    def __init__(self, model_type: str):
        self.model_type = model_type
        self.client = self._get_client()
    
    def _get_client(self) -> ChatCompletionsClient:
        return ChatCompletionsClient(
            endpoint=AIConfig.ENDPOINT,  # Updated reference
            credential=AzureKeyCredential(AIConfig.TOKEN)  # Updated reference
        )
    
    async def _execute_with_retry(self, func, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        for attempt in range(AIConfig.MAX_RETRIES):  # Updated reference
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == AIConfig.MAX_RETRIES - 1:  # Updated reference
                    logger.error(f"Max retries reached for {self.model_type}: {str(e)}")
                    raise
                await asyncio.sleep(AIConfig.RETRY_DELAY * (attempt + 1))  # Updated reference

class WebsiteGenerationService(BaseAIService):
    """Service for website generation using multiple AI models"""
    
    def __init__(self):
        self.frontend_service = BaseAIService("frontend")
        self.backend_service = BaseAIService("backend")
        self.tools = {
            "frontend": frontend_generator,
            "backend": backend_generator,
            "common": [internet_search, rag_query]
        }
    
    @lru_cache(maxsize=100)
    async def generate_website(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete website with caching"""
        cache_key = self._generate_cache_key(website_data)
        
        try:
            frontend_result = await self._generate_frontend(website_data)
            backend_result = await self._generate_backend(website_data)
            
            return {
                "frontend": frontend_result,
                "backend": backend_result,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Website generation failed: {str(e)}")
            raise
    
    async def _generate_frontend(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate frontend code using GPT-4o"""
        return await self.frontend_service._execute_with_retry(
            self._process_generation,
            data,
            "frontend",
            self.tools["frontend"]
        )
    
    async def _generate_backend(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate backend code using Codestral"""
        return await self.backend_service._execute_with_retry(
            self._process_generation,
            data,
            "backend",
            self.tools["backend"]
        )
    
    async def _process_generation(
        self,
        data: Dict[str, Any],
        generation_type: str,
        tool: Any
    ) -> Dict[str, str]:
        """Process generation request with RAG and internet search"""
        try:
            # Search knowledge base
            kb_results = await query_knowledge_base(data["description"])
            
            # Search internet for references
            search_results = await search_internet(data["description"])
            
            # Create enhanced prompt
            context = self._create_context(kb_results, search_results)
            
            messages = [
                SystemMessage(content=self._get_system_prompt(generation_type)),
                UserMessage(content=self._create_enhanced_prompt(data, context))
            ]
            
            response = await self._get_model_response(
                messages=messages,
                tools=[tool, internet_search, rag_query],
                model_type=generation_type
            )
            
            return self._process_response(response, generation_type)
            
        except Exception as e:
            logger.error(f"Enhanced generation failed: {str(e)}")
            raise
    
    def _create_context(
        self,
        kb_results: List[Dict[str, Any]],
        search_results: List[Dict[str, Any]]
    ) -> str:
        """Create context from search results"""
        context = []
        
        # Add knowledge base results
        if kb_results:
            context.append("From our knowledge base:")
            for result in kb_results[:3]:
                context.append(f"- {result['text']}")
        
        # Add internet search results
        if search_results:
            context.append("\nFrom internet search:")
            for result in search_results[:3]:
                context.append(f"- {result['snippet']}")
        
        return "\n".join(context)
    
    def _create_enhanced_prompt(
        self,
        data: Dict[str, Any],
        context: str
    ) -> str:
        """Create prompt with context"""
        return f"""
        Reference Information:
        {context}
        
        Based on the above context and these requirements:
        {self._create_prompt(data)}
        
        Generate appropriate code that follows best practices and modern standards.
        """
    
    async def _process_generation(
        self,
        data: Dict[str, Any],
        generation_type: str,
        tool: Any
    ) -> Dict[str, str]:
        """Process generation request"""
        messages = [
            SystemMessage(content=self._get_system_prompt(generation_type)),
            UserMessage(content=self._create_prompt(data, generation_type))
        ]
        
        response = await self._get_model_response(messages, tool, generation_type)
        return self._process_response(response, generation_type)
    
    def _get_system_prompt(self, generation_type: str) -> str:
        """Get system prompt based on generation type"""
        prompts = {
            "frontend": "You are a professional frontend developer expert in HTML, Tailwind CSS, and vanilla JavaScript.",
            "backend": "You are a professional Python backend developer expert in FastAPI/Flask and SQLAlchemy."
        }
        return prompts.get(generation_type, "You are a professional developer.")
    
    async def _get_model_response(self, messages: List[Any], tool: Any, model_type: str):
        """Get response from AI model"""
        client = self._get_client()
        return await client.complete(
            messages=messages,
            tools=[tool],
            model=AIConfig.MODELS[model_type]  # Updated reference
        )
    
    def _process_response(self, response: Any, generation_type: str) -> Dict[str, str]:
        """Process model response"""
        if response.choices[0].finish_reason == CompletionsFinishReason.TOOL_CALLS:
            tool_call = response.choices[0].message.tool_calls[0]
            if isinstance(tool_call, ChatCompletionsToolCall):
                return json.loads(tool_call.function.arguments)
        raise Exception(f"{generation_type} generation failed")
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        return f"website_gen_{hash(json.dumps(data, sort_keys=True))}"

class DocumentationService(BaseAIService):
    """Service for documentation generation using Llama"""
    
    def __init__(self):
        super().__init__("docs")
    
    async def generate_docs(self, website_data: Dict[str, Any]) -> str:
        """Generate documentation using Llama"""
        return await self._execute_with_retry(
            self._generate_documentation,
            website_data
        )
    
    async def _generate_documentation(self, data: Dict[str, Any]) -> str:
        messages = [
            SystemMessage(content="You are a technical documentation expert."),
            UserMessage(content=self._create_docs_prompt(data))
        ]
        
        response = await self.client.complete(
            messages=messages,
            model=AIConfig.MODELS["docs"]  # Updated reference
        )
        
        return response.choices[0].message.content

class DebugService(BaseAIService):
    """Service for debugging using Cohere"""
    
    def __init__(self):
        super().__init__("debug")
        self.debug_tool = debug_analyzer
    
    async def analyze_error(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze errors using Cohere"""
        return await self._execute_with_retry(
            self._analyze_error,
            error_data
        )
    
    async def _analyze_error(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            SystemMessage(content="You are an expert system debugger."),
            UserMessage(content=self._create_debug_prompt(error_data))
        ]
        
        response = await self.client.complete(
            messages=messages,
            tools=[self.debug_tool],
            model=AIConfig.MODELS["debug"]
        )
        
        if response.choices[0].finish_reason == CompletionsFinishReason.TOOL_CALLS:
            tool_call = response.choices[0].message.tool_calls[0]
            return json.loads(tool_call.function.arguments)
            
        raise Exception("Debug analysis failed")
