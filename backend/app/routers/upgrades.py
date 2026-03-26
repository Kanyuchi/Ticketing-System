import uuid

import stripe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.models.order import Order, OrderStatus, PaymentStatus
from app.services.upgrade_service import apply_upgrade, calculate_upgrade
from app.schemas.order import OrderOut

router = APIRouter(prefix="/upgrades", tags=["upgrades"])

stripe.api_key = settings.stripe_secret_key


class UpgradeRequest(BaseModel):
    order_id: uuid.UUID
    new_ticket_type_id: uuid.UUID
    discount_code: str | None = None


@router.post("/calculate")
async def calculate(data: UpgradeRequest, db: AsyncSession = Depends(get_db)):
    """Public: calculate upgrade price difference."""
    try:
        result = await calculate_upgrade(db, data.order_id, data.new_ticket_type_id, data.discount_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


@router.post("/checkout")
async def create_upgrade_checkout(data: UpgradeRequest, db: AsyncSession = Depends(get_db)):
    """Public: create Stripe checkout for the upgrade price difference."""
    try:
        calc = await calculate_upgrade(db, data.order_id, data.new_ticket_type_id, data.discount_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if calc["price_difference"] == 0:
        # Free upgrade, apply directly
        order = await apply_upgrade(db, data.order_id, data.new_ticket_type_id)
        return {"upgraded": True, "order_id": str(order.id)}

    # Get order for email
    result = await db.execute(
        select(Order).where(Order.id == data.order_id).options(selectinload(Order.attendee))
    )
    order = result.scalar_one()

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "unit_amount": calc["price_difference"],
                        "product_data": {
                            "name": f"Upgrade: {calc['current_ticket']} → {calc['new_ticket']}",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{settings.frontend_url}/order/{data.order_id}?status=upgraded",
            cancel_url=f"{settings.frontend_url}/order/{data.order_id}?status=cancelled",
            customer_email=order.attendee.email,
            metadata={
                "order_id": str(data.order_id),
                "new_ticket_type_id": str(data.new_ticket_type_id),
                "is_upgrade": "true",
            },
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"checkout_url": session.url, "session_id": session.id, "price_difference": calc["price_difference"]}
