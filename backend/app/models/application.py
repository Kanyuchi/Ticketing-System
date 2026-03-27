import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.types import GUID


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    ticket_type_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("ticket_types.id"), nullable=False
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, values_callable=lambda e: [x.value for x in e]),
        default=ApplicationStatus.PENDING,
    )

    # Applicant info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(String(255))
    reason: Mapped[str | None] = mapped_column(Text)  # why they should get this pass

    # Press-specific
    publication: Mapped[str | None] = mapped_column(String(255))  # media outlet name
    portfolio_url: Mapped[str | None] = mapped_column(String(500))  # link to work

    # Startup-specific
    startup_name: Mapped[str | None] = mapped_column(String(255))
    startup_website: Mapped[str | None] = mapped_column(String(500))
    startup_stage: Mapped[str | None] = mapped_column(String(100))  # pre-seed, seed, series A, etc.

    # On approval
    voucher_code: Mapped[str | None] = mapped_column(String(50))  # generated on approval for Press
    reviewed_by: Mapped[str | None] = mapped_column(String(255))  # admin email
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    ticket_type: Mapped["TicketType"] = relationship()
