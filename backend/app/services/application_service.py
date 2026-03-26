import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application, ApplicationStatus
from app.models.ticket_type import TicketType
from app.schemas.application import ApplicationSubmit, ApplicationReview
from app.services.voucher_service import bulk_create_vouchers


async def submit_application(db: AsyncSession, data: ApplicationSubmit) -> Application:
    # Verify ticket type exists and requires application
    result = await db.execute(select(TicketType).where(TicketType.id == data.ticket_type_id))
    ticket_type = result.scalar_one_or_none()
    if not ticket_type:
        raise ValueError("Ticket type not found")
    if not ticket_type.requires_application:
        raise ValueError("This ticket type does not require an application")

    # Check for duplicate application
    result = await db.execute(
        select(Application).where(
            Application.email == data.email,
            Application.ticket_type_id == data.ticket_type_id,
            Application.status != ApplicationStatus.REJECTED,
        )
    )
    if result.scalar_one_or_none():
        raise ValueError("You already have a pending or approved application for this ticket type")

    application = Application(**data.model_dump())
    db.add(application)
    await db.flush()

    # Reload with ticket_type relationship
    result = await db.execute(
        select(Application)
        .where(Application.id == application.id)
        .options(selectinload(Application.ticket_type))
    )
    return result.scalar_one()


async def review_application(
    db: AsyncSession,
    application_id: uuid.UUID,
    review: ApplicationReview,
    admin_email: str,
) -> Application:
    result = await db.execute(
        select(Application)
        .where(Application.id == application_id)
        .options(selectinload(Application.ticket_type))
    )
    application = result.scalar_one_or_none()
    if not application:
        raise ValueError("Application not found")
    if application.status != ApplicationStatus.PENDING:
        raise ValueError("Application has already been reviewed")

    application.status = review.status
    application.reviewed_by = admin_email
    application.reviewed_at = datetime.now(timezone.utc)

    if review.status == ApplicationStatus.REJECTED:
        application.rejection_reason = review.rejection_reason

    elif review.status == ApplicationStatus.APPROVED:
        # For complimentary passes (Press), generate a voucher code
        if application.ticket_type.is_complimentary:
            vouchers = await bulk_create_vouchers(
                db, application.ticket_type_id, "APPROVED", 1
            )
            application.voucher_code = vouchers[0].code

        # For paid passes (Startup), they'll be directed to purchase
        # No voucher needed — approval unlocks the purchase flow

    await db.flush()
    await db.refresh(application)
    return application


async def list_applications(
    db: AsyncSession,
    status: ApplicationStatus | None = None,
    ticket_type_id: uuid.UUID | None = None,
) -> list[Application]:
    query = (
        select(Application)
        .options(selectinload(Application.ticket_type))
        .order_by(Application.created_at.desc())
    )
    if status:
        query = query.where(Application.status == status)
    if ticket_type_id:
        query = query.where(Application.ticket_type_id == ticket_type_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_application(db: AsyncSession, application_id: uuid.UUID) -> Application | None:
    result = await db.execute(
        select(Application)
        .where(Application.id == application_id)
        .options(selectinload(Application.ticket_type))
    )
    return result.scalar_one_or_none()


async def get_application_by_email(
    db: AsyncSession, email: str, ticket_type_id: uuid.UUID
) -> Application | None:
    result = await db.execute(
        select(Application)
        .where(
            Application.email == email,
            Application.ticket_type_id == ticket_type_id,
        )
        .options(selectinload(Application.ticket_type))
        .order_by(Application.created_at.desc())
    )
    return result.scalars().first()
