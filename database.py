from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from enum import Enum
import faiss
import numpy as np
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define SubscriptionTier as proper Enum
class SubscriptionTier(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class VectorStore:
    """Enterprise-grade vector database management"""
    def __init__(self, dimension: int = 1024):
        self._init_vector_db(dimension)
        self._init_embedding_client()
        self.text_store = {}
    
    def _init_vector_db(self, dimension: int):
        """Initialize FAISS vector database"""
        try:
            self.index = faiss.IndexFlatL2(dimension)
            logger.info(f"Initialized FAISS index with dimension {dimension}")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {str(e)}")
            raise
    
    def _init_embedding_client(self):
        """Initialize Azure embedding client"""
        try:
            self.embedding_client = EmbeddingsClient(
                endpoint=os.getenv("AZURE_ENDPOINT", "https://models.inference.ai.azure.com"),
                credential=AzureKeyCredential(os.getenv("AZURE_TOKEN"))
            )
            self.model_name = "Cohere-embed-v3-multilingual"
            logger.info("Initialized embedding client")
        except Exception as e:
            logger.error(f"Failed to initialize embedding client: {str(e)}")
            raise
        
    async def add_texts(self, texts: List[str]) -> List[int]:
        """Add texts to vector store"""
        try:
            # Get embeddings
            response = self.embedding_client.embed(
                input=texts,
                model=self.model_name
            )
            
            # Convert to numpy array
            embeddings = np.array([item.embedding for item in response.data])
            
            # Generate IDs and add to FAISS
            ids = np.arange(len(self.text_store), len(self.text_store) + len(texts))
            self.index.add(embeddings)
            
            # Store original texts
            for i, text in zip(ids, texts):
                self.text_store[int(i)] = text
                
            return ids.tolist()
            
        except Exception as e:
            logger.error(f"Failed to add texts to vector store: {str(e)}")
            raise
    
    async def similarity_search(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search similar texts"""
        try:
            # Get query embedding
            query_response = self.embedding_client.embed(
                input=[query],
                model=self.model_name
            )
            query_embedding = np.array([query_response.data[0].embedding])
            
            # Search FAISS index
            D, I = self.index.search(query_embedding, k)
            
            # Format results
            results = []
            for score, idx in zip(D[0], I[0]):
                if idx in self.text_store:
                    results.append({
                        "id": int(idx),
                        "text": self.text_store[idx],
                        "score": float(score)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            raise

# Initialize vector store
vector_store = VectorStore()

# Initialize databases
def init_db():
    """Initialize all databases"""
    try:
        # Create SQL tables
        Base.metadata.create_all(bind=engine)
        logger.info("SQL database initialized successfully")
        
        # Verify vector store
        if vector_store.index is None:
            raise Exception("Vector store initialization failed")
        
        logger.info("All databases initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
