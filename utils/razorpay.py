import razorpay
from fastapi import HTTPException
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RazorpayClient:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
        )

    async def create_subscription(
        self,
        plan_id: str,
        customer_id: str,
        total_count: int = 12
    ) -> Dict[str, Any]:
        try:
            subscription = self.client.subscription.create({
                "plan_id": plan_id,
                "customer_id": customer_id,
                "total_count": total_count,
                "quantity": 1
            })
            return subscription
        except Exception as e:
            logger.error(f"Razorpay subscription creation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Subscription creation failed"
            )

    async def verify_payment(self, payment_id: str, signature: str, order_id: str) -> bool:
        try:
            self.client.utility.verify_payment_signature({
                'razorpay_signature': signature,
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id
            })
            return True
        except Exception:
            return False
