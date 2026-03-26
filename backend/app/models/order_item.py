import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.types import GUID


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("orders.id"), nullable=False
    )
    ticket_type_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("ticket_types.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price_eur: Mapped[int] = mapped_column(Integer, nullable=False)  # cents

    order: Mapped["Order"] = relationship(back_populates="items")
    ticket_type: Mapped["TicketType"] = relationship(back_populates="order_items")
