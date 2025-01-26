from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
import logging
from datetime import datetime

from models.subscription import Subscription, SubscriptionStatus
from services.notifications import send_subscription_notification

logger = logging.getLogger(__name__)

async def handle_subscription_activated(
    data: Dict[str, Any],
    db: Session,
    background_tasks: BackgroundTasks
) -> None:
    """Handle subscription activation webhook"""
    try:
        subscription_id = data["payload"]["subscription"]["id"]
        subscription = db.query(Subscription).filter(
            Subscription.razorpay_subscription_id == subscription_id
        ).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.current_period_start = datetime.utcnow()
            db.commit()
            
            background_tasks.add_task(
                send_subscription_notification,
                "activated",
                subscription.user_id
            )
    except Exception as e:
        logger.error(f"Subscription activation failed: {str(e)}")
        raise

async def handle_subscription_cancelled(
    data: Dict[str, Any],
    db: Session,
    background_tasks: BackgroundTasks
) -> None:
    """Handle subscription cancellation webhook"""
    try:
        subscription_id = data["payload"]["subscription"]["id"]
        subscription = db.query(Subscription).filter(
            Subscription.razorpay_subscription_id == subscription_id
        ).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.utcnow()
            db.commit()
            
            background_tasks.add_task(
                send_subscription_notification,
                "cancelled",
                subscription.user_id
            )
    except Exception as e:
        logger.error(f"Subscription cancellation failed: {str(e)}")
        raise

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from models.user import User, SubscriptionTier
from services.notifications import notify_subscription_change
from database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

async def handle_subscription_charged(
    user_id: str,
    subscription_data: Dict[str, Any],
    db: Optional[Session] = None
) -> None:
    """Handle successful subscription charge event"""
    try:
        if db is None:
            db = next(get_db())
            
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")
            
        # Update user subscription status
        user.subscription_tier = subscription_data.get('tier', SubscriptionTier.BASIC)
        user.last_payment_date = datetime.utcnow()
        db.commit()
        
        # Send notification
        await notify_subscription_change(
            user_id=user_id,
            tier=subscription_data['tier'],
            status="renewed"
        )
        
        logger.info(f"Subscription charged successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to handle subscription charge: {str(e)}")
        if db:
            db.rollback()
        raise

async def handle_subscription_failed(
    user_id: str,
    error_data: Dict[str, Any],
    db: Optional[Session] = None
) -> None:
    """Handle failed subscription charge event"""
    try:
        if db is None:
            db = next(get_db())
            
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")
            
        # Update subscription status
        user.subscription_tier = SubscriptionTier.BASIC
        db.commit()
        
        # Send notification
        await notify_subscription_change(
            user_id=user_id,
            tier=SubscriptionTier.BASIC,
            status="downgraded due to payment failure"
        )
        
        logger.warning(f"Subscription charge failed for user {user_id}: {error_data.get('reason')}")
        
    except Exception as e:
        logger.error(f"Failed to handle subscription failure: {str(e)}")
        if db:
            db.rollback()
        raise

async def handle_subscription_canceled(
    user_id: str,
    cancellation_data: Dict[str, Any],
    db: Optional[Session] = None
) -> None:
    """Handle subscription cancellation event"""
    try:
        if db is None:
            db = next(get_db())
            
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")
            
        # Update subscription status
        user.subscription_tier = SubscriptionTier.BASIC
        db.commit()
        
        # Send notification
        await notify_subscription_change(
            user_id=user_id,
            tier=SubscriptionTier.BASIC,
            status="canceled"
        )
        
        logger.info(f"Subscription canceled for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to handle subscription cancellation: {str(e)}")
        if db:
            db.rollback()
        raise

async def handle_subscription_changed(
    user_id: str,
    change_data: Dict[str, Any],
    db: Optional[Session] = None
) -> None:
    """Handle subscription plan change event"""
    try:
        if db is None:
            db = next(get_db())
            
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")
            
        # Update subscription tier
        new_tier = change_data.get('new_tier')
        if new_tier in [t.value for t in SubscriptionTier]:
            user.subscription_tier = new_tier
            db.commit()
            
            # Send notification
            await notify_subscription_change(
                user_id=user_id,
                tier=new_tier,
                status="changed"
            )
            
            logger.info(f"Subscription changed to {new_tier} for user {user_id}")
        else:
            raise ValueError(f"Invalid subscription tier: {new_tier}")
            
    except Exception as e:
        logger.error(f"Failed to handle subscription change: {str(e)}")
        if db:
            db.rollback()
        raise

async def handle_subscription_pending(
    user_id: str,
    pending_data: Dict[str, Any],
    db: Optional[Session] = None
) -> None:
    """Handle subscription pending event"""
    try:
        if db is None:
            db = next(get_db())
            
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")
            
        # Send notification about pending status
        await notify_subscription_change(
            user_id=user_id,
            tier=pending_data.get('tier', SubscriptionTier.BASIC),
            status="pending approval"
        )
        
        logger.info(f"Subscription pending for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to handle subscription pending: {str(e)}")
        if db:
            db.rollback()
        raise
