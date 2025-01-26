from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from models.user import User
logger = logging.getLogger(__name__)

class AnalyticsCalculator:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_monthly_revenue(self, month_start: datetime) -> float:
        """Calculate revenue for a specific month"""
        month_end = month_start + timedelta(days=32)
        month_end = month_end.replace(day=1)
        
        result = self.db.query(
            func.sum(SubscriptionPlan.price)
        ).join(
            Subscription,
            and_(
                Subscription.plan_id == SubscriptionPlan.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.current_period_start >= month_start,
                Subscription.current_period_start < month_end
            )
        ).scalar()
        
        return float(result or 0)
    
    async def get_ytd_revenue(self) -> float:
        """Calculate year-to-date revenue"""
        year_start = datetime.utcnow().replace(
            month=1, day=1, hour=0, minute=0, second=0
        )
        
        result = self.db.query(
            func.sum(SubscriptionPlan.price)
        ).join(
            Subscription,
            and_(
                Subscription.plan_id == SubscriptionPlan.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.current_period_start >= year_start
            )
        ).scalar()
        
        return float(result or 0)
    
    async def get_plan_popularity(self) -> List[Dict[str, Any]]:
        """Get subscription plan popularity metrics"""
        results = self.db.query(
            SubscriptionPlan,
            func.count(Subscription.id).label('total_subscriptions')
        ).join(
            Subscription,
            and_(
                Subscription.plan_id == SubscriptionPlan.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        ).group_by(SubscriptionPlan.id).all()
        
        return [
            {
                "plan_id": plan.id,
                "name": plan.name,
                "subscribers": total,
                "revenue": plan.price * total
            }
            for plan, total in results
        ]
    
    # ... implement other analytics methods ...
