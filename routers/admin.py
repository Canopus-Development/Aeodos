from fastapi import APIRouter, Depends, HTTPException, Security, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
import json

from database import get_db
from models.user import User
from models.subscription import (
    SubscriptionPlan, Subscription, SubscriptionStatus,
    SubscriptionPlanCreate, SubscriptionPlanResponse, SubscriptionPlanUpdate
)
from security import admin_required
from utils.analytics import AnalyticsCalculator

logger = logging.getLogger(__name__)

class AdminAnalytics:
    def __init__(self, db: Session):
        self.db = db
        self.calculator = AnalyticsCalculator(db)
    
    async def calculate_revenue(self) -> Dict[str, Any]:
        """Calculate revenue analytics"""
        try:
            current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
            
            # Get monthly revenue
            monthly_revenue = await self.calculator.get_monthly_revenue(current_month)
            
            # Get YTD revenue
            ytd_revenue = await self.calculator.get_ytd_revenue()
            
            # Get projected revenue
            projected_revenue = await self.calculator.get_projected_revenue()
            
            return {
                "current_month": monthly_revenue,
                "ytd": ytd_revenue,
                "projected": projected_revenue,
                "growth_rate": await self.calculator.get_revenue_growth_rate()
            }
        except Exception as e:
            logger.error(f"Revenue calculation failed: {str(e)}")
            raise
    
    async def calculate_user_growth(self) -> Dict[str, Any]:
        """Calculate user growth analytics"""
        try:
            return {
                "total_users": await self.calculator.get_total_users(),
                "active_users": await self.calculator.get_active_users(),
                "growth_rate": await self.calculator.get_user_growth_rate(),
                "churn_rate": await self.calculator.get_churn_rate(),
                "retention_rate": await self.calculator.get_retention_rate()
            }
        except Exception as e:
            logger.error(f"User growth calculation failed: {str(e)}")
            raise
    
    async def get_popular_plans(self) -> List[Dict[str, Any]]:
        """Get popular subscription plans"""
        try:
            return await self.calculator.get_plan_popularity()
        except Exception as e:
            logger.error(f"Plan popularity calculation failed: {str(e)}")
            raise

router = APIRouter(prefix="/aeodos/admin", tags=["admin"])

@router.post(
    "/plans",
    response_model=SubscriptionPlanResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)]
)
async def create_subscription_plan(
    plan: SubscriptionPlanCreate,
    db: Session = Depends(get_db)
):
    """Create new subscription plan"""
    try:
        # Check if plan name already exists
        if db.query(SubscriptionPlan).filter(SubscriptionPlan.name == plan.name).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan with this name already exists"
            )
        
        # Create new plan
        db_plan = SubscriptionPlan(
            name=plan.name,
            description=plan.description,
            price=plan.price,
            interval=plan.interval,
            features=json.dumps(plan.features),
            is_active=plan.is_active
        )
        
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        
        # Convert features back to list for response
        db_plan.features = json.loads(db_plan.features)
        return db_plan
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create subscription plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/analytics", dependencies=[Depends(admin_required)])
async def get_analytics(db: Session = Depends(get_db)):
    """Get platform analytics"""
    try:
        analytics = AdminAnalytics(db)
        
        return {
            "total_users": db.query(User).count(),
            "active_subscriptions": db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.ACTIVE
            ).count(),
            "revenue": await analytics.calculate_revenue(),
            "user_growth": await analytics.calculate_user_growth(),
            "popular_plans": await analytics.get_popular_plans()
        }
    except Exception as e:
        logger.error(f"Analytics retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/blocked", dependencies=[Depends(admin_required)])
async def get_blocked_users(db: Session = Depends(get_db)):
    """Get list of blocked users"""
    return db.query(User).filter(User.is_blocked == True).all()
