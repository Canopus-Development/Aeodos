from azure.ai.inference.models import ChatCompletionsToolDefinition, FunctionDefinition
from typing import Dict, Any, List
import json
import logging
from enum import Enum
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class WebsiteStyle(str, Enum):
    MODERN = "modern"
    MINIMAL = "minimal"
    CORPORATE = "corporate"
    CREATIVE = "creative"
    E_COMMERCE = "e-commerce"

class ColorScheme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    CUSTOM = "custom"
    BRAND = "brand"

class BusinessType(str, Enum):
    RETAIL = "retail"
    SERVICE = "service"
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    GENERAL = "general"

# Frontend Generator Tool
frontend_generator = ChatCompletionsToolDefinition(
    function=FunctionDefinition(
        name="generate_frontend",
        description="Generates professional website frontend using HTML, Tailwind CSS and vanilla JavaScript",
        parameters={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Website name",
                    "minLength": 3,
                    "maxLength": 50
                },
                "business_type": {
                    "type": "string",
                    "description": "Type of business",
                    "enum": [t.value for t in BusinessType]
                },
                "style": {
                    "type": "string",
                    "description": "Website style",
                    "enum": [s.value for s in WebsiteStyle]
                },
                "description": {
                    "type": "string",
                    "description": "Website description",
                    "minLength": 10,
                    "maxLength": 500
                },
                "color_scheme": {
                    "type": "string",
                    "description": "Color scheme preferences",
                    "enum": [c.value for c in ColorScheme]
                },
                "features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of required features",
                    "default": []
                },
                "seo_metadata": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "keywords": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "required": ["name", "description"]
        }
    )
)

# Backend Generator Tool
backend_generator = ChatCompletionsToolDefinition(
    function=FunctionDefinition(
        name="generate_backend",
        description="Generates Python FastAPI backend code for the website",
        parameters={
            "type": "object",
            "properties": {
                "endpoints": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                            "description": {"type": "string"},
                            "authentication": {"type": "boolean", "default": True}
                        },
                        "required": ["path", "method"]
                    }
                },
                "features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Required backend features"
                },
                "database_models": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "fields": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "type": {"type": "string"},
                                        "required": {"type": "boolean"}
                                    }
                                }
                            }
                        }
                    }
                },
                "security": {
                    "type": "object",
                    "properties": {
                        "authentication": {"type": "boolean", "default": True},
                        "rate_limiting": {"type": "boolean", "default": True},
                        "cors_enabled": {"type": "boolean", "default": True}
                    }
                }
            },
            "required": ["endpoints"]
        }
    )
)

# Debug Analyzer Tool
debug_analyzer = ChatCompletionsToolDefinition(
    function=FunctionDefinition(
        name="analyze_error",
        description="Analyzes errors in website generation and provides solutions",
        parameters={
            "type": "object",
            "properties": {
                "error_message": {
                    "type": "string",
                    "description": "The error message to analyze"
                },
                "error_type": {
                    "type": "string",
                    "description": "Type of error",
                    "enum": [
                        "syntax",
                        "runtime",
                        "logical",
                        "security",
                        "performance",
                        "compatibility",
                        "other"
                    ]
                },
                "context": {
                    "type": "object",
                    "properties": {
                        "component": {"type": "string"},
                        "file_path": {"type": "string"},
                        "line_number": {"type": "integer"},
                        "stack_trace": {"type": "string"},
                        "environment": {"type": "object"}
                    }
                },
                "suggested_fixes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "code_change": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    }
                }
            },
            "required": ["error_message"]
        }
    )
)

# Internet Search Tool
internet_search = ChatCompletionsToolDefinition(
    function=FunctionDefinition(
        name="search_internet",
        description="Search the internet for relevant information",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }
    )
)

# RAG Query Tool
rag_query = ChatCompletionsToolDefinition(
    function=FunctionDefinition(
        name="query_knowledge_base",
        description="Query the vector database for relevant information",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for knowledge base"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    )
)

def validate_tool_input(tool: ChatCompletionsToolDefinition, data: Dict[str, Any]) -> bool:
    """Validate input data against tool schema"""
    try:
        parameters = tool.function.parameters
        required = parameters.get("required", [])
        
        # Check required fields
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate field types and constraints
        properties = parameters.get("properties", {})
        for field, value in data.items():
            if field in properties:
                field_schema = properties[field]
                _validate_field(field, value, field_schema)
        
        return True
        
    except Exception as e:
        logger.error(f"Tool input validation failed: {str(e)}")
        raise ValueError(f"Invalid tool input: {str(e)}")

def _validate_field(field_name: str, value: Any, schema: Dict[str, Any]) -> None:
    """Validate individual field against its schema"""
    field_type = schema.get("type")
    
    if field_type == "string":
        if not isinstance(value, str):
            raise ValueError(f"Field {field_name} must be a string")
        
        min_length = schema.get("minLength")
        max_length = schema.get("maxLength")
        enum_values = schema.get("enum")
        
        if min_length and len(value) < min_length:
            raise ValueError(f"Field {field_name} must be at least {min_length} characters")
        if max_length and len(value) > max_length:
            raise ValueError(f"Field {field_name} must be at most {max_length} characters")
        if enum_values and value not in enum_values:
            raise ValueError(f"Field {field_name} must be one of: {', '.join(enum_values)}")
    
    elif field_type == "array":
        if not isinstance(value, list):
            raise ValueError(f"Field {field_name} must be an array")
        
        item_schema = schema.get("items", {})
        for item in value:
            if item_schema.get("type") == "object":
                for key, val in item.items():
                    if key in item_schema.get("properties", {}):
                        _validate_field(f"{field_name}.{key}", val, item_schema["properties"][key])
            else:
                _validate_field(f"{field_name}[]", item, item_schema)
    
    elif field_type == "object":
        if not isinstance(value, dict):
            raise ValueError(f"Field {field_name} must be an object")
        
        for key, val in value.items():
            if key in schema.get("properties", {}):
                _validate_field(f"{field_name}.{key}", val, schema["properties"][key])

async def search_internet(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """Search internet using DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
            return [
                {
                    "title": result["title"],
                    "link": result["link"],
                    "snippet": result["body"]  # Changed from 'snippet' to 'body'
                }
                for result in results
            ]
    except Exception as e:
        logger.error(f"Internet search failed: {str(e)}")
        raise

async def query_knowledge_base(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """Query vector store for relevant information"""
    try:
        from database import vector_store
        return await vector_store.similarity_search(query, k=num_results)
    except Exception as e:
        logger.error(f"Knowledge base query failed: {str(e)}")
        raise
