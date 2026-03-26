import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.models.application import ApplicationStatus
from app.routers.auth import get_current_admin
from app.schemas.application import ApplicationOut, ApplicationReview, ApplicationSubmit
from app.services.application_service import (
    get_application,
    list_applications,
    review_application,
    submit_application,
)

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut, status_code=201)
async def submit(data: ApplicationSubmit, db: AsyncSession = Depends(get_db)):
    """Public: submit an application for a Startup or Press pass."""
    try:
        application = await submit_application(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Send confirmation email
    from app.services.email_service import send_application_received
    await send_application_received(application.email, application.name, application.ticket_type.name)

    return application


@router.get("", response_model=list[ApplicationOut])
async def list_all(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    status: ApplicationStatus | None = Query(None),
    ticket_type_id: uuid.UUID | None = Query(None),
):
    """Admin: list applications with optional filters."""
    return await list_applications(db, status, ticket_type_id)


@router.get("/{application_id}", response_model=ApplicationOut)
async def get_detail(application_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Public: check application status."""
    app = await get_application(db, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.post("/{application_id}/review", response_model=ApplicationOut)
async def review(
    application_id: uuid.UUID,
    data: ApplicationReview,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: approve or reject an application."""
    try:
        application = await review_application(db, application_id, data, admin.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Send email based on decision
    from app.services.email_service import send_application_approved, send_application_rejected
    if application.status == ApplicationStatus.APPROVED:
        await send_application_approved(
            application.email,
            application.name,
            application.ticket_type.name,
            application.voucher_code,
            application.ticket_type.is_complimentary,
        )
    elif application.status == ApplicationStatus.REJECTED:
        await send_application_rejected(
            application.email,
            application.name,
            application.ticket_type.name,
            application.rejection_reason,
        )

    return application
