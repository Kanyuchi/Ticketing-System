import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.order import Order, OrderStatus, PaymentStatus

router = APIRouter(prefix="/payments", tags=["payments"])

stripe.api_key = settings.stripe_secret_key


@router.post("/create-checkout/{order_id}")
async def create_checkout_session(order_id: str, db: AsyncSession = Depends(get_db)):
    """Create a Stripe checkout session for an unpaid order."""
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.attendee), selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.payment_status != PaymentStatus.UNPAID:
        raise HTTPException(status_code=400, detail="Order is not awaiting payment")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "unit_amount": order.total_eur,
                        "product_data": {"name": f"Proof of Talk 2026 - Order {order.order_number}"},
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{settings.frontend_url}/order/{order.id}?status=success",
            cancel_url=f"{settings.frontend_url}/order/{order.id}?status=cancelled",
            customer_email=order.attendee.email,
            metadata={"order_id": str(order.id)},
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    order.stripe_session_id = session.id
    await db.flush()

    return {"checkout_url": session.url, "session_id": session.id}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session["metadata"].get("order_id")
        if order_id:
            result = await db.execute(select(Order).where(Order.id == order_id))
            order = result.scalar_one_or_none()
            if order:
                order.status = OrderStatus.CONFIRMED
                order.payment_status = PaymentStatus.PAID
                order.stripe_payment_intent = session.get("payment_intent")
                await db.flush()

    return {"status": "ok"}
