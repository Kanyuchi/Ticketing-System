import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.types import GUID


class Referral(Base):
    """A referral code/link owned by an ambassador or attendee."""
    __tablename__ = "referrals"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    orders_count: Mapped[int] = mapped_column(Integer, default=0)
    revenue_eur: Mapped[int] = mapped_column(Integer, default=0)  # cents
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    attributions: Mapped[list["ReferralAttribution"]] = relationship(back_populates="referral")


class ReferralAttribution(Base):
    """Links an order to the referral that drove it."""
    __tablename__ = "referral_attributions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    referral_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("referrals.id"), nullable=False
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("orders.id"), nullable=False, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    referral: Mapped["Referral"] = relationship(back_populates="attributions")
    order: Mapped["Order"] = relationship()
