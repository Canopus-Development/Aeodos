import os
from typing import Dict, Any, Optional
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import ChatCompletionsClient
from fastapi import HTTPException

class AIConfig:
    AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT", "https://models.inference.ai.azure.com")
    TOKEN = os.getenv("AZURE_TOKEN")
    
    if not TOKEN:
        raise ValueError("AZURE_TOKEN environment variable is required")
    
    MODELS = {
        "frontend": "gpt-4o",
        "backend": "Codestral-2501",
        "debug": "Cohere-command-r-plus",
        "docs": "Llama-3.3-70B-Instruct"
    }
    
    _clients: Dict[str, ChatCompletionsClient] = {}

    @classmethod
    def get_client(cls, model_type: str) -> ChatCompletionsClient:
        if model_type not in cls.MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model type: {model_type}"
            )
        
        if model_type not in cls._clients:
            cls._clients[model_type] = ChatCompletionsClient(
                endpoint=cls.AZURE_ENDPOINT,
                credential=AzureKeyCredential(cls.TOKEN),
            )
        
        return cls._clients[model_type]
