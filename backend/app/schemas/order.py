import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.order import OrderStatus, PaymentStatus
from app.schemas.attendee import AttendeeOut


class OrderItemCreate(BaseModel):
    ticket_type_id: uuid.UUID
    quantity: int = 1


class OrderCreate(BaseModel):
    attendee: "AttendeeCreateInline"
    items: list[OrderItemCreate]
    voucher_code: str | None = None


class AttendeeCreateInline(BaseModel):
    email: EmailStr
    name: str
    company: str | None = None
    title: str | None = None


class OrderItemOut(BaseModel):
    id: uuid.UUID
    ticket_type_id: uuid.UUID
    quantity: int
    unit_price_eur: int

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: uuid.UUID
    order_number: str
    attendee: AttendeeOut
    status: OrderStatus
    payment_status: PaymentStatus
    total_eur: int
    voucher_code: str | None
    items: list[OrderItemOut]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderFilter(BaseModel):
    voucher_code: str | None = None
    name: str | None = None
    ticket_type: str | None = None
    email: str | None = None
    company: str | None = None
    order_status: OrderStatus | None = None
    payment_status: PaymentStatus | None = None
