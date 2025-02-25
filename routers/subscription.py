from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from utils.razorpay import RazorpayClient
from security import verify_api_key
from services.subscription_handlers import (
    handle_subscription_activated,
    handle_subscription_cancelled,
    handle_subscription_charged,
    handle_subscription_pending
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/Aoede/subscription",
    tags=["subscription"]
)

@router.post("/upgrade")
async def upgrade_subscription(
    plan_id: str,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Upgrade user subscription"""
    try:
        user = db.query(User).filter(User.api_key == api_key).first()
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()

        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        razorpay = RazorpayClient()
        subscription = await razorpay.create_subscription(
            plan_id=plan.razorpay_plan_id,
            customer_id=user.razorpay_customer_id
        )

        new_subscription = Subscription(
            user_id=user.id,
            plan_id=plan.id,
            razorpay_subscription_id=subscription["id"],
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )

        db.add(new_subscription)
        db.commit()

        return {
            "subscription_id": subscription["id"],
            "payment_link": subscription["short_url"]
        }

    except Exception as e:
        logger.error(f"Subscription upgrade failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def handle_subscription_webhook(
    data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Razorpay webhook events"""
    event_type = data.get("event")
    
    handlers = {
        "subscription.activated": handle_subscription_activated,
        "subscription.cancelled": handle_subscription_cancelled,
        "subscription.charged": handle_subscription_charged,
        "subscription.pending": handle_subscription_pending
    }
    
    handler = handlers.get(event_type)
    if handler:
        await handler(data, db, background_tasks)
    
    return {"status": "processed"}
