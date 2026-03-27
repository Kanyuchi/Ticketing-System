import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.types import GUID


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    COMPLIMENTARY = "complimentary"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    attendee_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("attendees.id"), nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, values_callable=lambda e: [x.value for x in e]),
        default=OrderStatus.PENDING,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, values_callable=lambda e: [x.value for x in e]),
        default=PaymentStatus.UNPAID,
    )
    total_eur: Mapped[int] = mapped_column(Integer, default=0)  # cents
    stripe_session_id: Mapped[str | None] = mapped_column(String(255))
    stripe_payment_intent: Mapped[str | None] = mapped_column(String(255))
    voucher_code: Mapped[str | None] = mapped_column(String(50), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    attendee: Mapped["Attendee"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
