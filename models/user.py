from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLAlchemyEnum
from datetime import datetime
from enum import Enum
from database import Base

class SubscriptionTier(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class User(Base):
    """User model with subscription information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String)  # Company name
    api_key = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    requests_count = Column(Integer, default=0)
    subscription_tier = Column(SQLAlchemyEnum(SubscriptionTier), default=SubscriptionTier.BASIC)
    key_regenerated_at = Column(DateTime, nullable=True)
    last_project_generated = Column(DateTime, nullable=True)
    projects_generated_count = Column(Integer, default=0)

    @property
    def is_premium(self) -> bool:
        """Check if user has premium access"""
        return self.subscription_tier in [SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE]
    
    @property
    def is_enterprise(self) -> bool:
        """Check if user has enterprise access"""
        return self.subscription_tier == SubscriptionTier.ENTERPRISE
    
    def increment_request_count(self) -> None:
        """Increment the request counter"""
        self.requests_count += 1
