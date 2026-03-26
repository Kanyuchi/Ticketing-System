import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.types import GUID


class Voucher(Base):
    __tablename__ = "vouchers"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    ticket_type_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("ticket_types.id"), nullable=False
    )
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    used_by_email: Mapped[str | None] = mapped_column(String(255))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    ticket_type: Mapped["TicketType"] = relationship(back_populates="vouchers")
