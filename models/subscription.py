from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from database import Base

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PENDING = "pending"
    EXPIRED = "expired"
    FAILED = "failed"

class SubscriptionInterval(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

# SQLAlchemy Models
class SubscriptionPlan(Base):
    """Database model for subscription plans"""
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Float)
    interval = Column(SQLAlchemyEnum(SubscriptionInterval))
    features = Column(String)  # JSON string of features
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Subscription(Base):
    """Database model for user subscriptions"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    status = Column(SQLAlchemyEnum(SubscriptionStatus))
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    plan = relationship("SubscriptionPlan")
    user = relationship("User")

# Pydantic Models for API
class SubscriptionPlanCreate(BaseModel):
    """Schema for creating subscription plans"""
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)
    price: float = Field(..., gt=0)
    interval: SubscriptionInterval
    features: list[str] = Field(..., min_items=1)
    is_active: bool = True

class SubscriptionPlanResponse(BaseModel):
    """Schema for subscription plan responses"""
    id: int
    name: str
    description: str
    price: float
    interval: SubscriptionInterval
    features: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SubscriptionPlanUpdate(BaseModel):
    """Schema for updating subscription plans"""
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    interval: Optional[SubscriptionInterval] = None
    features: Optional[list[str]] = Field(None, min_items=1)
    is_active: Optional[bool] = None
