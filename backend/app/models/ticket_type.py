import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.types import GUID


class TicketCategory(str, enum.Enum):
    SPEAKER = "speaker"
    PARTNER = "partner"
    PRESS = "press"
    VIP = "vip"
    VIP_BLACK = "vip_black"
    GENERAL = "general"
    INVESTOR = "investor"
    STARTUP = "startup"


class TicketType(Base):
    __tablename__ = "ticket_types"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[TicketCategory] = mapped_column(
        Enum(TicketCategory, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    price_eur: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # cents
    is_complimentary: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_application: Mapped[bool] = mapped_column(Boolean, default=False)
    quantity_total: Mapped[int | None] = mapped_column(Integer)
    quantity_sold: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="ticket_type")
    vouchers: Mapped[list["Voucher"]] = relationship(back_populates="ticket_type")
