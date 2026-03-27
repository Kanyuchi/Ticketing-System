import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.types import GUID


class CheckIn(Base):
    """Records attendance check-in for a confirmed order."""
    __tablename__ = "check_ins"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("orders.id"), nullable=False, unique=True, index=True
    )
    checked_in_by: Mapped[str | None] = mapped_column(String(255))  # admin email
    device_id: Mapped[str | None] = mapped_column(String(100))  # for offline sync
    notes: Mapped[str | None] = mapped_column(Text)
    is_synced: Mapped[bool] = mapped_column(Boolean, default=True)
    checked_in_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    order: Mapped["Order"] = relationship()
